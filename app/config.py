import os

class Config:
    """Configuración base"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'clave-secreta-por-defecto'
    CACHE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'cache'))
    LOG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'logs'))
    CACHE_TIMEOUT = 24 * 60 * 60  # 24 horas en segundos

class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    TESTING = False
    # Mayor tiempo de caché para reducir peticiones en producción
    CACHE_TIMEOUT = 48 * 60 * 60  # 48 horas en segundos
    # Otras configuraciones específicas para producción
class TestingConfig(Config):
    """Configuración para pruebas"""
    DEBUG = True
    TESTING = True
    CACHE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'tests', 'cache'))