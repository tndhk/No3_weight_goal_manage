from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Data(db.Model):
    """
    データモデルの定義
    
    属性:
        id (int): データのプライマリーキー
        name (str): データの名前
        value (float): データの値
        category (str): データのカテゴリ
        created_at (datetime): データ作成日時
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    value = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, name, value, category):
        self.name = name
        self.value = value
        self.category = category

    def to_dict(self):
        """
        モデルをJSONシリアライズ可能な辞書に変換
        
        戻り値:
            dict: モデルの属性を含む辞書
        """
        return {
            'id': self.id,
            'name': self.name,
            'value': self.value,
            'category': self.category,
            'created_at': self.created_at.isoformat()
        }

    def __repr__(self):
        return f'<Data {self.id}: {self.name}>'