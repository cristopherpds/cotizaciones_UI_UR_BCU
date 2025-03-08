import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from flask_swagger_ui import get_swaggerui_blueprint

# Cargar variables de entorno desde .env
load_dotenv()

def create_app(config_name=None):
    app = Flask(__name__)
    CORS(app)
    
    # Configuración según entorno (desarrollo, producción, etc.)
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    # Cargar configuración según el entorno
    if config_name == 'production':
        app.config.from_object('app.config.ProductionConfig')
    else:
        app.config.from_object('app.config.DevelopmentConfig')
    
    # Sobreescribir con variables de entorno si existen
    if os.environ.get('SECRET_KEY'):
        app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    if os.environ.get('CACHE_TIMEOUT'):
        app.config['CACHE_TIMEOUT'] = int(os.environ.get('CACHE_TIMEOUT'))
    
    # Crear directorios necesarios si no existen
    os.makedirs(app.config['CACHE_DIR'], exist_ok=True)
    os.makedirs(app.config['LOG_DIR'], exist_ok=True)
    
    # Configurar logging
    from app.utils.logger import setup_logger
    setup_logger(app.config['LOG_DIR'])
    
    # Registrar blueprints (rutas de la API)
    from app.api.routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Configurar Swagger UI
    from app.api.swagger import swagger_bp
    app.register_blueprint(swagger_bp, url_prefix='/api')
    
    # Configurar Swagger UI blueprint
    SWAGGER_URL = '/docs'  # URL for exposing Swagger UI
    API_URL = '/api/swagger.json'  # URL for swagger.json endpoint
    
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': "BCU Exchange Rate API"
        }
    )
    
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
    
    return app