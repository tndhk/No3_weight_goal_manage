import os
from flask_swagger_ui import get_swaggerui_blueprint

def register_swagger(app):
    """
    アプリケーションにSwagger UIを登録する
    
    引数:
        app (Flask): Flaskアプリケーションインスタンス
    """
    # OpenAPIスキーマファイルのパス
    openapi_path = os.path.join(app.root_path, 'static')
    os.makedirs(openapi_path, exist_ok=True)
    
    # OpenAPIスキーマファイルへのルートを追加
    @app.route('/api/spec')
    def get_spec():
        with open(os.path.join(openapi_path, 'openapi.yaml'), 'r', encoding='utf-8') as f:
            return f.read(), 200, {'Content-Type': 'text/yaml'}
    
    # Swagger UIのパスと設定
    swagger_url = '/api/docs'
    api_url = '/api/spec'
    
    # Swagger UIブループリントを作成
    swaggerui_blueprint = get_swaggerui_blueprint(
        swagger_url,
        api_url,
        config={
            'app_name': "Fitbit Weight Tracker API"
        }
    )
    
    # アプリケーションに登録
    app.register_blueprint(swaggerui_blueprint, url_prefix=swagger_url)