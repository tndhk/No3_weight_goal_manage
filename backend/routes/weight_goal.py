from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
from models import db, WeightGoal, FitbitWeight
from sqlalchemy import func

weight_goal_api = Blueprint('weight_goal_api', __name__)

@weight_goal_api.route('/goal', methods=['POST'])
def create_goal():
    """
    体重目標を作成するエンドポイント
    
    リクエスト:
        JSON: target_weight, target_date, description(オプション)を含む
    
    戻り値:
        JSON: 作成された目標
    """
    try:
        data = request.json
        user_id = 'default_user'  # 本番環境では認証システムと連携
        
        # 必須フィールドの検証
        if 'target_weight' not in data or 'target_date' not in data:
            return jsonify({'error': 'target_weight and target_date are required'}), 400
            
        # 日付のパース
        try:
            target_date = datetime.strptime(data['target_date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
            
        # 開始体重の取得（最新の体重データ）
        latest_weight = FitbitWeight.query.filter_by(user_id=user_id).order_by(FitbitWeight.date.desc()).first()
        start_weight = latest_weight.weight if latest_weight else data.get('start_weight')
        
        if not start_weight:
            return jsonify({'error': 'No weight data available and no start_weight provided'}), 400
            
        # 目標の作成
        new_goal = WeightGoal(
            user_id=user_id,
            target_weight=float(data['target_weight']),
            target_date=target_date,
            start_weight=float(start_weight),
            start_date=datetime.now().date(),
            description=data.get('description')
        )
        
        db.session.add(new_goal)
        db.session.commit()
        
        return jsonify(new_goal.to_dict()), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@weight_goal_api.route('/goal', methods=['GET'])
def get_goals():
    """
    ユーザーの体重目標を取得するエンドポイント
    
    クエリパラメータ:
        active_only (bool): trueの場合、達成済みでない目標のみを返す
        
    戻り値:
        JSON: 目標のリスト
    """
    try:
        user_id = 'default_user'  # 本番環境では認証システムと連携
        active_only = request.args.get('active_only', 'false').lower() == 'true'
        
        # クエリを構築
        query = WeightGoal.query.filter_by(user_id=user_id)
        
        if active_only:
            query = query.filter_by(is_achieved=False)
            
        # 結果を取得
        goals = query.order_by(WeightGoal.target_date).all()
        
        return jsonify([goal.to_dict() for goal in goals])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@weight_goal_api.route('/goal/<int:goal_id>', methods=['GET'])
def get_goal(goal_id):
    """
    特定の体重目標を取得するエンドポイント
    
    引数:
        goal_id (int): 目標のID
        
    戻り値:
        JSON: 指定されたIDの目標
    """
    try:
        user_id = 'default_user'  # 本番環境では認証システムと連携
        goal = WeightGoal.query.filter_by(id=goal_id, user_id=user_id).first_or_404()
        
        return jsonify(goal.to_dict())
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@weight_goal_api.route('/goal/<int:goal_id>', methods=['PUT'])
def update_goal(goal_id):
    """
    体重目標を更新するエンドポイント
    
    引数:
        goal_id (int): 更新する目標のID
    
    リクエスト:
        JSON: 更新するフィールド（target_weight, target_date, description, is_achieved）
        
    戻り値:
        JSON: 更新された目標
    """
    try:
        user_id = 'default_user'  # 本番環境では認証システムと連携
        goal = WeightGoal.query.filter_by(id=goal_id, user_id=user_id).first_or_404()
        data = request.json
        
        # 更新可能なフィールド
        if 'target_weight' in data:
            goal.target_weight = float(data['target_weight'])
            
        if 'target_date' in data:
            goal.target_date = datetime.strptime(data['target_date'], '%Y-%m-%d').date()
            
        if 'description' in data:
            goal.description = data['description']
            
        if 'is_achieved' in data:
            goal.is_achieved = bool(data['is_achieved'])
            if goal.is_achieved and not goal.achieved_date:
                goal.achieved_date = datetime.now().date()
                
        db.session.commit()
        
        return jsonify(goal.to_dict())
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@weight_goal_api.route('/goal/<int:goal_id>', methods=['DELETE'])
def delete_goal(goal_id):
    """
    体重目標を削除するエンドポイント
    
    引数:
        goal_id (int): 削除する目標のID
        
    戻り値:
        JSON: 削除の成功メッセージ
    """
    try:
        user_id = 'default_user'  # 本番環境では認証システムと連携
        goal = WeightGoal.query.filter_by(id=goal_id, user_id=user_id).first_or_404()
        
        db.session.delete(goal)
        db.session.commit()
        
        return jsonify({'message': f'Goal {goal_id} deleted'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@weight_goal_api.route('/weight/diff', methods=['GET'])
def get_weight_diff():
    """
    実測値と目標の差分を取得するエンドポイント
    
    クエリパラメータ:
        goal_id (int): 目標のID（指定しない場合はアクティブな目標を使用）
    
    戻り値:
        JSON: 差分データ
    """
    try:
        user_id = 'default_user'  # 本番環境では認証システムと連携
        goal_id = request.args.get('goal_id')
        
        # 目標の取得
        if goal_id:
            goal = WeightGoal.query.filter_by(id=goal_id, user_id=user_id).first_or_404()
        else:
            # アクティブな目標を取得（期限が最も近いもの）
            goal = WeightGoal.query.filter_by(
                user_id=user_id, 
                is_achieved=False
            ).order_by(WeightGoal.target_date).first()
            
            if not goal:
                return jsonify({'error': 'No active goal found'}), 404
        
        # 開始日から目標日までの期間
        start_date = goal.start_date
        target_date = goal.target_date
        
        # 期間内の体重データを取得
        weights = FitbitWeight.query.filter(
            FitbitWeight.user_id == user_id,
            FitbitWeight.date >= start_date,
            FitbitWeight.date <= datetime.now().date()
        ).order_by(FitbitWeight.date).all()
        
        # 目標達成のための毎日の理想体重変化
        if target_date <= start_date:
            daily_target_change = 0
        else:
            total_days = (target_date - start_date).days
            total_change = goal.target_weight - goal.start_weight
            daily_target_change = total_change / total_days if total_days > 0 else 0
        
        # 理想の体重推移と実際の体重を比較
        weight_diffs = []
        current_date = start_date
        end_date = min(datetime.now().date(), target_date)
        
        # 日付ごとのループ
        while current_date <= end_date:
            # 目標体重を計算
            days_since_start = (current_date - start_date).days
            target_weight_for_day = goal.start_weight + (daily_target_change * days_since_start)
            
            # 実際の体重データを検索
            actual_weight = next(
                (w.weight for w in weights if w.date == current_date), 
                None
            )
            
            # 差分を計算
            if actual_weight is not None:
                diff = actual_weight - target_weight_for_day
            else:
                diff = None
                
            weight_diffs.append({
                'date': current_date.isoformat(),
                'target_weight': round(target_weight_for_day, 1),
                'actual_weight': actual_weight,
                'difference': round(diff, 1) if diff is not None else None
            })
            
            current_date += timedelta(days=1)
        
        # 現在の進行状況
        latest_weight = FitbitWeight.query.filter_by(user_id=user_id).order_by(FitbitWeight.date.desc()).first()
        current_weight = latest_weight.weight if latest_weight else None
        
        # レスポンスデータの構築
        response = {
            'goal': goal.to_dict(),
            'current_weight': current_weight,
            'weight_to_lose': round(current_weight - goal.target_weight, 1) if current_weight else None,
            'days_remaining': (target_date - datetime.now().date()).days,
            'daily_weight_diffs': weight_diffs,
            'avg_actual_change_per_day': _calculate_avg_change(weights) if weights else None
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@weight_goal_api.route('/weight/projection', methods=['GET'])
def get_weight_projection():
    """
    現在の進捗から将来の体重を予測するエンドポイント
    
    クエリパラメータ:
        goal_id (int): 目標のID（指定しない場合はアクティブな目標を使用）
        days (int): 予測したい将来の日数（デフォルト: 30）
    
    戻り値:
        JSON: 予測データ
    """
    try:
        user_id = 'default_user'  # 本番環境では認証システムと連携
        goal_id = request.args.get('goal_id')
        days = int(request.args.get('days', 30))
        
        # 目標の取得
        if goal_id:
            goal = WeightGoal.query.filter_by(id=goal_id, user_id=user_id).first_or_404()
        else:
            # アクティブな目標を取得（期限が最も近いもの）
            goal = WeightGoal.query.filter_by(
                user_id=user_id, 
                is_achieved=False
            ).order_by(WeightGoal.target_date).first()
            
            if not goal:
                return jsonify({'error': 'No active goal found'}), 404
        
        # 過去7日間の体重データを取得して平均変化率を計算
        one_week_ago = datetime.now().date() - timedelta(days=7)
        recent_weights = FitbitWeight.query.filter(
            FitbitWeight.user_id == user_id,
            FitbitWeight.date >= one_week_ago
        ).order_by(FitbitWeight.date).all()
        
        # 最新の体重データを取得
        latest_weight_record = FitbitWeight.query.filter_by(user_id=user_id).order_by(FitbitWeight.date.desc()).first()
        latest_weight = latest_weight_record.weight if latest_weight_record else goal.start_weight
        
        # 今日の日付
        today = datetime.now().date()
        
        # データが不十分な場合はデフォルト値を使用
        if len(recent_weights) < 2:
            # 十分なデータがない場合は、理想的な予測を返す（目標に向かって直線）
            total_days = (goal.target_date - today).days
            if total_days <= 0:
                # 目標日が過ぎている場合
                avg_change_per_day = 0
            else:
                weight_to_change = goal.target_weight - latest_weight
                avg_change_per_day = weight_to_change / total_days
            
            # 予測データを生成
            projections = []
            current_weight = latest_weight
            
            for i in range(1, days + 1):
                projection_date = today + timedelta(days=i)
                current_weight += avg_change_per_day
                
                projections.append({
                    'date': projection_date.isoformat(),
                    'projected_weight': round(current_weight, 1)
                })
            
            return jsonify({
                'goal': goal.to_dict(),
                'latest_weight': latest_weight,
                'avg_change_per_day': avg_change_per_day,
                'projected_completion_date': goal.target_date.isoformat(),
                'weight_projections': projections,
                'insufficient_data': True
            })
        
        # 十分なデータがある場合は実際の変化率を計算
        avg_change_per_day = _calculate_avg_change(recent_weights)
        
        # 予測データを生成
        projections = []
        current_weight = latest_weight
        
        for i in range(1, days + 1):
            projection_date = today + timedelta(days=i)
            current_weight += avg_change_per_day
            
            projections.append({
                'date': projection_date.isoformat(),
                'projected_weight': round(current_weight, 1)
            })
        
        # 予測達成日の計算
        if (goal.target_weight > goal.start_weight and avg_change_per_day > 0) or \
           (goal.target_weight < goal.start_weight and avg_change_per_day < 0):
            weight_to_change = goal.target_weight - latest_weight
            days_to_goal = abs(weight_to_change / avg_change_per_day) if avg_change_per_day != 0 else float('inf')
            projected_completion_date = today + timedelta(days=round(days_to_goal))
        else:
            projected_completion_date = None
        
        return jsonify({
            'goal': goal.to_dict(),
            'latest_weight': latest_weight,
            'avg_change_per_day': avg_change_per_day,
            'projected_completion_date': projected_completion_date.isoformat() if projected_completion_date else None,
            'weight_projections': projections,
            'insufficient_data': False
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e), 'trace': traceback.format_exc()}), 400
    
def _calculate_avg_change(weights):
    """
    体重変化の1日あたりの平均変化率を計算
    
    引数:
        weights (list): 体重データのリスト
        
    戻り値:
        float: 1日あたりの平均変化率
    """
    if len(weights) < 2:
        return 0
        
    first_weight = weights[0]
    last_weight = weights[-1]
    
    total_change = last_weight.weight - first_weight.weight
    days = (last_weight.date - first_weight.date).days
    
    if days == 0:
        return 0
        
    return total_change / days