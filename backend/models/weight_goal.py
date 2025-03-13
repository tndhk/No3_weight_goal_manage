from datetime import datetime
from .data_model import db

class WeightGoal(db.Model):
    """
    体重目標データモデル
    
    インデックス:
        idx_weight_goal_user_id: user_id列のインデックス
        idx_weight_goal_target_date: target_date列のインデックス
        idx_weight_goal_is_achieved: is_achieved列のインデックス
    
    属性:
        id (int): プライマリーキー
        user_id (str): ユーザー識別子
        target_weight (float): 目標体重
        target_date (date): 目標達成予定日
        start_weight (float): 開始時の体重
        start_date (date): 目標設定日
        description (str): 目標の説明・メモ
        is_achieved (bool): 達成フラグ
        achieved_date (date): 達成日
        created_at (datetime): レコード作成日時
        updated_at (datetime): レコード最終更新日時
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), nullable=False)
    target_weight = db.Column(db.Float, nullable=False)
    target_date = db.Column(db.Date, nullable=False)
    start_weight = db.Column(db.Float, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    is_achieved = db.Column(db.Boolean, default=False)
    achieved_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # インデックスを定義
    __table_args__ = (
        db.Index('idx_weight_goal_user_id', 'user_id'),
        db.Index('idx_weight_goal_target_date', 'target_date'),
        db.Index('idx_weight_goal_is_achieved', 'is_achieved'),
    )
    
    def __init__(self, user_id, target_weight, target_date, start_weight=None, start_date=None, description=None):
        self.user_id = user_id
        self.target_weight = target_weight
        self.target_date = target_date
        self.start_weight = start_weight
        self.start_date = start_date or datetime.now().date()
        self.description = description
    
    def to_dict(self):
        """
        モデルをJSONシリアライズ可能な辞書に変換
        
        戻り値:
            dict: モデルの属性を含む辞書
        """
        return {
            'id': self.id,
            'user_id': self.user_id,
            'target_weight': self.target_weight,
            'target_date': self.target_date.isoformat() if self.target_date else None,
            'start_weight': self.start_weight,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'description': self.description,
            'is_achieved': self.is_achieved,
            'achieved_date': self.achieved_date.isoformat() if self.achieved_date else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'days_remaining': (self.target_date - datetime.now().date()).days if self.target_date else None,
            'progress_percentage': self._calculate_progress() if not self.is_achieved else 100
        }
    
    def _calculate_progress(self):
        """
        目標達成の進捗率を計算
        
        戻り値:
            float: 進捗率（0〜100）
        """
        if self.is_achieved:
            return 100.0
            
        try:
            from models import FitbitWeight
            
            # 最新の体重を取得
            latest_weight = FitbitWeight.query.filter_by(user_id=self.user_id).order_by(FitbitWeight.date.desc()).first()
            
            if not latest_weight:
                return 0.0
                
            # 開始体重と目標体重の差分
            total_diff = abs(self.start_weight - self.target_weight)
            
            if total_diff == 0:
                return 100.0
                
            # 現在の体重と目標体重の差分
            current_diff = abs(latest_weight.weight - self.target_weight)
            
            # 進捗率を計算（減量・増量どちらにも対応）
            progress = ((total_diff - current_diff) / total_diff) * 100
            
            # 0〜100の範囲に制限
            return max(0, min(100, progress))
        except Exception:
            # 計算エラーの場合は0を返す
            return 0.0
    
    def __repr__(self):
        return f'<WeightGoal {self.id}: {self.user_id} - {self.target_weight}kg by {self.target_date}>'