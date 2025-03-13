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