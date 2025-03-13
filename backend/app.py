from flask import Flask, jsonify, request, session
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import shutil

from models import db, Data, FitbitAuth, FitbitWeight, WeightGoal
from routes import api, fitbit_api, weight_goal_api
from config import get_config
from swagger import register_swagger

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
    app.register_blueprint(weight_goal_api, url_prefix='/api/fit')
    
    # セッションシークレットキー
    app.secret_key = app.config['SECRET_KEY']
    
    with app.app_context():
        # instance ディレクトリの存在を確認
        os.makedirs('/app/instance', exist_ok=True)
        db.create_all()
        
        # OpenAPIスキーマファイルをコピー
        static_dir = os.path.join(app.root_path, 'static')
        os.makedirs(static_dir, exist_ok=True)
        
        openapi_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'openapi.yaml')
        if os.path.exists(openapi_file):
            shutil.copy(openapi_file, os.path.join(static_dir, 'openapi.yaml'))
    
    # Swagger UIを登録
    register_swagger(app)
    
    return app

app = create_app()

@app.route('/')
def index():
    return jsonify({'message': 'Welcome to the Flask-React-SQLite API'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')