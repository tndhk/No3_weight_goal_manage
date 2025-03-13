from datetime import datetime
from .data_model import db

class FitbitWeight(db.Model):
    """
    Fitbit体重データモデル
    
    属性:
        id (int): プライマリーキー
        user_id (str): ユーザー識別子
        weight (float): 体重
        bmi (float): BMI
        date (date): 記録日
        time (time): 記録時間
        source (str): データソース
        log_id (str): Fitbitログ識別子
        created_at (datetime): レコード作成日時
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), nullable=False)
    weight = db.Column(db.Float, nullable=False)
    bmi = db.Column(db.Float, nullable=True)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=True)
    source = db.Column(db.String(100), nullable=True)
    log_id = db.Column(db.String(100), nullable=True, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """
        モデルをJSONシリアライズ可能な辞書に変換
        
        戻り値:
            dict: モデルの属性を含む辞書
        """
        return {
            'id': self.id,
            'user_id': self.user_id,
            'weight': self.weight,
            'bmi': self.bmi,
            'date': self.date.isoformat() if self.date else None,
            'time': self.time.isoformat() if self.time else None,
            'source': self.source,
            'log_id': self.log_id,
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<FitbitWeight {self.id}: {self.user_id} - {self.date}>'