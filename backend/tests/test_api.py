import pytest
import json
import os
import tempfile
from app import app, db, Data

@pytest.fixture
def client():
    """テスト用のクライアントを作成する"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()

def test_index(client):
    """インデックスエンドポイントのテスト"""
    response = client.get('/')
    data = json.loads(response.data)
    assert response.status_code == 200
    assert 'message' in data

def test_get_all_data_empty(client):
    """空のデータリスト取得テスト"""
    response = client.get('/api/data')
    data = json.loads(response.data)
    assert response.status_code == 200
    assert isinstance(data, list)
    assert len(data) == 0

def test_add_data(client):
    """データ追加テスト"""
    test_data = {
        'name': 'Test Item',
        'value': 100.5,
        'category': 'Test Category'
    }
    response = client.post(
        '/api/data',
        data=json.dumps(test_data),
        content_type='application/json'
    )
    data = json.loads(response.data)
    assert response.status_code == 201
    assert data['name'] == 'Test Item'
    assert data['value'] == 100.5
    assert data['category'] == 'Test Category'
    assert 'id' in data
    assert 'created_at' in data

def test_get_all_data_with_items(client):
    """データ追加後のリスト取得テスト"""
    # テストデータの追加
    test_data = {
        'name': 'Test Item',
        'value': 100.5,
        'category': 'Test Category'
    }
    client.post(
        '/api/data',
        data=json.dumps(test_data),
        content_type='application/json'
    )
    
    # データを取得してテスト
    response = client.get('/api/data')
    data = json.loads(response.data)
    assert response.status_code == 200
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]['name'] == 'Test Item'

def test_get_data_by_id(client):
    """IDによるデータ取得テスト"""
    # テストデータの追加
    test_data = {
        'name': 'Test Item',
        'value': 100.5,
        'category': 'Test Category'
    }
    response = client.post(
        '/api/data',
        data=json.dumps(test_data),
        content_type='application/json'
    )
    data = json.loads(response.data)
    id = data['id']
    
    # IDでデータを取得
    response = client.get(f'/api/data/{id}')
    data = json.loads(response.data)
    assert response.status_code == 200
    assert data['id'] == id
    assert data['name'] == 'Test Item'

def test_update_data(client):
    """データ更新テスト"""
    # テストデータの追加
    test_data = {
        'name': 'Test Item',
        'value': 100.5,
        'category': 'Test Category'
    }
    response = client.post(
        '/api/data',
        data=json.dumps(test_data),
        content_type='application/json'
    )
    data = json.loads(response.data)
    id = data['id']
    
    # データを更新
    update_data = {
        'name': 'Updated Item',
        'value': 200.5
    }
    response = client.put(
        f'/api/data/{id}',
        data=json.dumps(update_data),
        content_type='application/json'
    )
    data = json.loads(response.data)
    assert response.status_code == 200
    assert data['id'] == id
    assert data['name'] == 'Updated Item'
    assert data['value'] == 200.5
    assert data['category'] == 'Test Category'  # 未更新のフィールド

def test_delete_data(client):
    """データ削除テスト"""
    # テストデータの追加
    test_data = {
        'name': 'Test Item',
        'value': 100.5,
        'category': 'Test Category'
    }
    response = client.post(
        '/api/data',
        data=json.dumps(test_data),
        content_type='application/json'
    )
    data = json.loads(response.data)
    id = data['id']
    
    # データを削除
    response = client.delete(f'/api/data/{id}')
    assert response.status_code == 200
    
    # 削除したデータが存在しないことを確認
    response = client.get(f'/api/data/{id}')
    assert response.status_code == 404

def test_analytics(client):
    """アナリティクスデータ取得テスト"""
    # テストデータを追加
    test_data1 = {
        'name': 'Item 1',
        'value': 100.5,
        'category': 'Category A'
    }
    test_data2 = {
        'name': 'Item 2',
        'value': 200.5,
        'category': 'Category B'
    }
    client.post(
        '/api/data',
        data=json.dumps(test_data1),
        content_type='application/json'
    )
    client.post(
        '/api/data',
        data=json.dumps(test_data2),
        content_type='application/json'
    )
    
    # アナリティクスデータを取得
    response = client.get('/api/analytics')
    data = json.loads(response.data)
    assert response.status_code == 200
    assert isinstance(data, list)
    assert len(data) == 2