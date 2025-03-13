from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

# データベース設定を修正 - 絶対パスを使用
# instance_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance')
# app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(instance_path, "app.db")}'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////app/instance/app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# データモデル
class Data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    value = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'value': self.value,
            'category': self.category,
            'created_at': self.created_at.isoformat()
        }

# データベース作成
with app.app_context():
    # instance ディレクトリの存在を確認
    os.makedirs('/app/instance', exist_ok=True)
    db.create_all()

# ルート
@app.route('/')
def index():
    return jsonify({'message': 'Welcome to the Flask-React-SQLite API'})

# すべてのデータを取得
@app.route('/api/data', methods=['GET'])
def get_all_data():
    data = Data.query.all()
    return jsonify([item.to_dict() for item in data])

# 新しいデータを追加
@app.route('/api/data', methods=['POST'])
def add_data():
    try:
        data = request.json
        new_item = Data(
            name=data['name'],
            value=float(data['value']),
            category=data['category']
        )
        db.session.add(new_item)
        db.session.commit()
        return jsonify(new_item.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# 特定のデータを取得
@app.route('/api/data/<int:id>', methods=['GET'])
def get_data(id):
    item = Data.query.get_or_404(id)
    return jsonify(item.to_dict())

# データを更新
@app.route('/api/data/<int:id>', methods=['PUT'])
def update_data(id):
    try:
        item = Data.query.get_or_404(id)
        data = request.json
        
        if 'name' in data:
            item.name = data['name']
        if 'value' in data:
            item.value = float(data['value'])
        if 'category' in data:
            item.category = data['category']
            
        db.session.commit()
        return jsonify(item.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# データを削除
@app.route('/api/data/<int:id>', methods=['DELETE'])
def delete_data(id):
    try:
        item = Data.query.get_or_404(id)
        db.session.delete(item)
        db.session.commit()
        return jsonify({'message': f'Item {id} deleted'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# アナリティクスデータを取得
@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    data = Data.query.all()
    return jsonify([item.to_dict() for item in data])

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')