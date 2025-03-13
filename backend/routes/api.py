from flask import Blueprint, jsonify, request
from models import db, Data

api = Blueprint('api', __name__)

@api.route('/data', methods=['GET'])
def get_all_data():
    """
    すべてのデータを取得するエンドポイント
    
    戻り値:
        JSON: データのリスト
    """
    data = Data.query.all()
    return jsonify([item.to_dict() for item in data])

@api.route('/data', methods=['POST'])
def add_data():
    """
    新しいデータを追加するエンドポイント
    
    リクエスト:
        JSON: name, value, category を含む
    
    戻り値:
        JSON: 作成されたデータ
    """
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

@api.route('/data/<int:id>', methods=['GET'])
def get_data(id):
    """
    特定のIDのデータを取得するエンドポイント
    
    引数:
        id (int): データのID
        
    戻り値:
        JSON: 指定されたIDのデータ
    """
    item = Data.query.get_or_404(id)
    return jsonify(item.to_dict())

@api.route('/data/<int:id>', methods=['PUT'])
def update_data(id):
    """
    既存のデータを更新するエンドポイント
    
    引数:
        id (int): 更新するデータのID
    
    リクエスト:
        JSON: 更新するフィールド（name, value, category）
        
    戻り値:
        JSON: 更新されたデータ
    """
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

@api.route('/data/<int:id>', methods=['DELETE'])
def delete_data(id):
    """
    データを削除するエンドポイント
    
    引数:
        id (int): 削除するデータのID
        
    戻り値:
        JSON: 削除の成功メッセージ
    """
    try:
        item = Data.query.get_or_404(id)
        db.session.delete(item)
        db.session.commit()
        return jsonify({'message': f'Item {id} deleted'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@api.route('/analytics', methods=['GET'])
def get_analytics():
    """
    アナリティクス用のデータを取得するエンドポイント
    
    戻り値:
        JSON: アナリティクスデータ
    """
    data = Data.query.all()
    return jsonify([item.to_dict() for item in data])