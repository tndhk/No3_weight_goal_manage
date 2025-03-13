from datetime import datetime
from .data_model import db

class FitbitAuth(db.Model):
    """
    Fitbit認証データモデル
    
    属性:
        id (int): プライマリーキー
        user_id (str): ユーザー識別子（将来的に複数ユーザー対応のため）
        access_token (str): Fitbit APIアクセストークン
        refresh_token (str): リフレッシュトークン
        expires_at (datetime): アクセストークンの有効期限
        scope (str): 許可されたスコープ
        token_type (str): トークンタイプ（通常は "Bearer"）
        created_at (datetime): レコード作成日時
        updated_at (datetime): レコード最終更新日時
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), nullable=False, unique=True)
    access_token = db.Column(db.Text, nullable=False)
    refresh_token = db.Column(db.Text, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    scope = db.Column(db.String(255), nullable=False)
    token_type = db.Column(db.String(50), nullable=False, default='Bearer')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def is_token_expired(self):
        """
        トークンが期限切れかどうかを確認
        
        戻り値:
            bool: 期限切れならTrue、有効ならFalse
        """
        return datetime.utcnow() > self.expires_at
    
    def to_dict(self):
        """
        モデルをJSONシリアライズ可能な辞書に変換
        
        戻り値:
            dict: モデルの属性を含む辞書
        """
        return {
            'id': self.id,
            'user_id': self.user_id,
            'expires_at': self.expires_at.isoformat(),
            'scope': self.scope,
            'token_type': self.token_type,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<FitbitAuth {self.id}: {self.user_id}>'