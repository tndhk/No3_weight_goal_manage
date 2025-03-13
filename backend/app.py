from flask import Flask, jsonify, request, session
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

from models import db, Data, FitbitAuth, FitbitWeight
from routes import api, fitbit_api
from config import get_config

def create_app():
    app = Flask(__name__)
    # 設定を適用
    app.config.from_object(get_config())
    
    # CORSを有効化
    CORS(app)
    
    # データベースを初期化
    db.init_app(app)
    
    # ルートを登録
    app.register_blueprint(api, url_prefix='/api')
    app.register_blueprint(fitbit_api, url_prefix='/api/fitbit')
    
    # セッションシークレットキー
    app.secret_key = app.config['SECRET_KEY']
    
    with app.app_context():
        # instance ディレクトリの存在を確認
        os.makedirs('/app/instance', exist_ok=True)
        db.create_all()
    
    return app

app = create_app()

@app.route('/')
def index():
    return jsonify({'message': 'Welcome to the Flask-React-SQLite API'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')