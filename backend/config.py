import os
from dotenv import load_dotenv

# .env ファイルがあれば読み込み
load_dotenv()

class Config:
    # 一般設定
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-please-change-in-production'
    
    # データベース設定
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///instance/app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 実行環境
    ENV = os.environ.get('FLASK_ENV') or 'production'
    
    # Fitbit API設定
    FITBIT_CLIENT_ID = os.environ.get('FITBIT_CLIENT_ID')
    FITBIT_CLIENT_SECRET = os.environ.get('FITBIT_CLIENT_SECRET')
    FITBIT_REDIRECT_URI = os.environ.get('FITBIT_REDIRECT_URI', 'http://localhost:5000/api/fitbit/callback')
    FITBIT_AUTHORIZATION_URL = 'https://www.fitbit.com/oauth2/authorize'
    FITBIT_TOKEN_URL = 'https://api.fitbit.com/oauth2/token'
    FITBIT_API_BASE_URL = 'https://api.fitbit.com'

class DevelopmentConfig(Config):
    DEBUG = True
    ENV = 'development'

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///instance/test.db'

class ProductionConfig(Config):
    # 本番環境固有の設定
    pass

# 環境に応じた設定を選択
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

def get_config():
    """現在の環境に基づいて設定を取得"""
    env = os.environ.get('FLASK_ENV', 'default')
    return config.get(env, config['default'])