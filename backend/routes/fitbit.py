from flask import Blueprint, jsonify, request, redirect, url_for, current_app, session
import requests
import base64
import json
from datetime import datetime, timedelta
from urllib.parse import urlencode
import secrets
from models import db, FitbitAuth, FitbitWeight

fitbit_api = Blueprint('fitbit_api', __name__)

# OAuth2.0認証フローのための状態トークン
@fitbit_api.route('/auth', methods=['GET'])
def auth():
    """
    Fitbit認証フローを開始するエンドポイント
    
    戻り値:
        リダイレクト: Fitbit認証サーバーへのリダイレクト
    """
    # ステートトークンを生成（CSRF対策）
    state = secrets.token_urlsafe(16)
    session['fitbit_oauth_state'] = state
    
    # 認証パラメータの設定
    params = {
        'response_type': 'code',
        'client_id': current_app.config['FITBIT_CLIENT_ID'],
        'redirect_uri': current_app.config['FITBIT_REDIRECT_URI'],
        'scope': 'weight',  # 体重データにアクセスするスコープ
        'state': state
    }
    
    # Fitbit認証URLにリダイレクト
    authorization_url = f"{current_app.config['FITBIT_AUTHORIZATION_URL']}?{urlencode(params)}"
    return redirect(authorization_url)

@fitbit_api.route('/callback', methods=['GET'])
def callback():
    """
    Fitbit認証コールバックエンドポイント
    
    戻り値:
        JSON: 認証結果
    """
    # リクエストパラメータから認可コードとステートを取得
    code = request.args.get('code')
    state = request.args.get('state')
    error = request.args.get('error')
    
    # エラーまたはステート不一致の場合は認証失敗
    if error or not state or state != session.get('fitbit_oauth_state'):
        return jsonify({'success': False, 'error': error or 'Invalid state'}), 400
    
    # クリア済みのCSRFトークン
    session.pop('fitbit_oauth_state', None)
    
    # トークン取得のためのリクエスト
    token_url = current_app.config['FITBIT_TOKEN_URL']
    
    # クライアントIDとシークレットを使用した認証
    client_id = current_app.config['FITBIT_CLIENT_ID']
    client_secret = current_app.config['FITBIT_CLIENT_SECRET']
    auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    
    headers = {
        'Authorization': f'Basic {auth_header}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    data = {
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': current_app.config['FITBIT_REDIRECT_URI']
    }
    
    # トークン取得
    try:
        response = requests.post(token_url, headers=headers, data=data)
        response.raise_for_status()
        token_data = response.json()
        
        # トークンの有効期限を計算
        expires_at = datetime.utcnow() + timedelta(seconds=token_data['expires_in'])
        
        # 仮のユーザーID（本番環境では認証システムと連携）
        user_id = 'default_user'
        
        # 既存の認証情報があるか確認
        auth_record = FitbitAuth.query.filter_by(user_id=user_id).first()
        
        # 認証情報の保存または更新
        if auth_record:
            auth_record.access_token = token_data['access_token']
            auth_record.refresh_token = token_data['refresh_token']
            auth_record.expires_at = expires_at
            auth_record.scope = token_data['scope']
            auth_record.token_type = token_data['token_type']
        else:
            auth_record = FitbitAuth(
                user_id=user_id,
                access_token=token_data['access_token'],
                refresh_token=token_data['refresh_token'],
                expires_at=expires_at,
                scope=token_data['scope'],
                token_type=token_data['token_type']
            )
            db.session.add(auth_record)
        
        db.session.commit()
        
        # フロントエンドにリダイレクト（成功）
        return redirect(f"http://localhost:3000/fitbit/success")
        
    except requests.exceptions.RequestException as e:
        # エラーハンドリング
        error_message = str(e)
        if hasattr(e, 'response') and e.response:
            try:
                error_data = e.response.json()
                error_message = error_data.get('errors', [{}])[0].get('message', str(e))
            except:
                pass
        
        # フロントエンドにリダイレクト（失敗）
        return redirect(f"http://localhost:3000/fitbit/error?message={error_message}")

# リフレッシュトークンを使用してアクセストークンを更新
def refresh_access_token(auth_record):
    """
    リフレッシュトークンを使用してアクセストークンを更新
    
    引数:
        auth_record (FitbitAuth): 更新する認証レコード
        
    戻り値:
        bool: 更新成功ならTrue、失敗ならFalse
    """
    token_url = current_app.config['FITBIT_TOKEN_URL']
    
    # クライアントIDとシークレットを使用した認証
    client_id = current_app.config['FITBIT_CLIENT_ID']
    client_secret = current_app.config['FITBIT_CLIENT_SECRET']
    auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    
    headers = {
        'Authorization': f'Basic {auth_header}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': auth_record.refresh_token
    }
    
    try:
        response = requests.post(token_url, headers=headers, data=data)
        response.raise_for_status()
        token_data = response.json()
        
        # トークンの有効期限を計算
        expires_at = datetime.utcnow() + timedelta(seconds=token_data['expires_in'])
        
        # 認証情報の更新
        auth_record.access_token = token_data['access_token']
        auth_record.refresh_token = token_data['refresh_token']
        auth_record.expires_at = expires_at
        auth_record.scope = token_data['scope']
        auth_record.token_type = token_data['token_type']
        
        db.session.commit()
        return True
        
    except requests.exceptions.RequestException:
        return False

# 有効なアクセストークンを取得（必要に応じて更新）
def get_valid_access_token(user_id='default_user'):
    """
    有効なアクセストークンを取得（必要に応じて更新）
    
    引数:
        user_id (str): ユーザー識別子
        
    戻り値:
        str または None: 有効なアクセストークン、または取得失敗時はNone
    """
    auth_record = FitbitAuth.query.filter_by(user_id=user_id).first()
    
    if not auth_record:
        return None
    
    # トークンが期限切れの場合は更新
    if auth_record.is_token_expired():
        success = refresh_access_token(auth_record)
        if not success:
            return None
    
    return auth_record.access_token

# 認証状態チェックエンドポイント
@fitbit_api.route('/status', methods=['GET'])
def status():
    """
    Fitbit認証状態を確認するエンドポイント
    
    戻り値:
        JSON: 認証状態
    """
    user_id = 'default_user'  # 本番環境では認証システムと連携
    
    auth_record = FitbitAuth.query.filter_by(user_id=user_id).first()
    
    if not auth_record:
        return jsonify({
            'is_authenticated': False,
            'message': 'Not authenticated with Fitbit'
        })
    
    # トークンの期限切れ確認
    if auth_record.is_token_expired():
        success = refresh_access_token(auth_record)
        if not success:
            return jsonify({
                'is_authenticated': False,
                'message': 'Authentication expired and refresh failed'
            })
    
    return jsonify({
        'is_authenticated': True,
        'expires_at': auth_record.expires_at.isoformat(),
        'scope': auth_record.scope
    })

# 体重データ取得エンドポイント
@fitbit_api.route('/weight', methods=['GET'])
def get_weight():
    """
    Fitbitから体重データを取得するエンドポイント
    
    クエリパラメータ:
        from_date (str): 開始日 (YYYY-MM-DD)
        to_date (str): 終了日 (YYYY-MM-DD)
        
    戻り値:
        JSON: 体重データ
    """
    # 期間指定（デフォルトは過去30日）
    today = datetime.now().strftime('%Y-%m-%d')
    from_date = request.args.get('from_date', (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
    to_date = request.args.get('to_date', today)
    
    # ユーザーIDを取得（本番環境では認証システムと連携）
    user_id = 'default_user'
    
    # アクセストークンを取得
    access_token = get_valid_access_token(user_id)
    if not access_token:
        return jsonify({
            'success': False,
            'error': 'Not authenticated with Fitbit or token refresh failed'
        }), 401
    
    # Fitbit APIから体重データを取得
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    url = f"{current_app.config['FITBIT_API_BASE_URL']}/1/user/-/body/log/weight/date/{from_date}/{to_date}.json"
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        weight_data = response.json()
        
        # データベースに保存
        weight_entries = []
        for entry in weight_data.get('weight', []):
            # 日時の処理
            log_date = datetime.strptime(entry.get('date', ''), '%Y-%m-%d').date()
            log_time = None
            if 'time' in entry:
                time_str = entry.get('time', '')
                try:
                    log_time = datetime.strptime(time_str, '%H:%M:%S').time()
                except ValueError:
                    pass
            
            # 既存のエントリを確認
            existing = FitbitWeight.query.filter_by(log_id=str(entry.get('logId'))).first()
            
            if not existing:
                new_entry = FitbitWeight(
                    user_id=user_id,
                    weight=entry.get('weight'),
                    bmi=entry.get('bmi'),
                    date=log_date,
                    time=log_time,
                    source=entry.get('source'),
                    log_id=str(entry.get('logId'))
                )
                db.session.add(new_entry)
                weight_entries.append(new_entry)
        
        if weight_entries:
            db.session.commit()
        
        # 同期後にデータベースから取得（保存されたすべてのデータを含む）
        stored_data = FitbitWeight.query.filter(
            FitbitWeight.user_id == user_id,
            FitbitWeight.date >= from_date,
            FitbitWeight.date <= to_date
        ).order_by(FitbitWeight.date, FitbitWeight.time).all()
        
        return jsonify({
            'success': True,
            'data': [entry.to_dict() for entry in stored_data]
        })
        
    except requests.exceptions.RequestException as e:
        error_message = str(e)
        status_code = 500
        
        # レスポンスがあればエラー詳細を取得
        if hasattr(e, 'response') and e.response:
            status_code = e.response.status_code
            try:
                error_data = e.response.json()
                error_message = error_data.get('errors', [{}])[0].get('message', str(e))
            except:
                pass
        
        # APIレート制限の場合
        if status_code == 429:
            return jsonify({
                'success': False,
                'error': 'Fitbit API rate limit exceeded. Please try again later.'
            }), 429
        
        # 認証エラーの場合
        if status_code in (401, 403):
            return jsonify({
                'success': False,
                'error': 'Authentication failed. Please reauthenticate with Fitbit.'
            }), status_code
        
        return jsonify({
            'success': False,
            'error': f'Error fetching weight data: {error_message}'
        }), status_code

# データ分析エンドポイント
@fitbit_api.route('/weight/analysis', methods=['GET'])
def analyze_weight():
    """
    体重データの分析を行うエンドポイント
    
    クエリパラメータ:
        from_date (str): 開始日 (YYYY-MM-DD)
        to_date (str): 終了日 (YYYY-MM-DD)
        
    戻り値:
        JSON: 分析結果
    """
    # 期間指定（デフォルトは過去30日）
    today = datetime.now().strftime('%Y-%m-%d')
    from_date = request.args.get('from_date', (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
    to_date = request.args.get('to_date', today)
    
    # ユーザーIDを取得（本番環境では認証システムと連携）
    user_id = 'default_user'
    
    # データベースから体重データを取得
    weight_data = FitbitWeight.query.filter(
        FitbitWeight.user_id == user_id,
        FitbitWeight.date >= from_date,
        FitbitWeight.date <= to_date
    ).order_by(FitbitWeight.date, FitbitWeight.time).all()
    
    if not weight_data:
        return jsonify({
            'success': False,
            'error': 'No weight data available for the specified period'
        }), 404
    
    # 分析データの準備
    weights = [entry.weight for entry in weight_data if entry.weight]
    dates = [entry.date.isoformat() for entry in weight_data]
    
    # 基本的な統計データ
    analysis = {
        'count': len(weights),
        'min_weight': min(weights) if weights else None,
        'max_weight': max(weights) if weights else None,
        'avg_weight': sum(weights) / len(weights) if weights else None,
        'start_weight': weights[0] if weights else None,
        'end_weight': weights[-1] if weights else None,
        'change': weights[-1] - weights[0] if len(weights) > 1 else 0,
        'period': {
            'from_date': from_date,
            'to_date': to_date
        },
        'chart_data': [
            {'date': date, 'weight': weight}
            for date, weight in zip(dates, weights)
        ]
    }
    
    return jsonify({
        'success': True,
        'analysis': analysis
    })