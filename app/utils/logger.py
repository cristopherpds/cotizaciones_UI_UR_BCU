import os
import logging
from logging.handlers import RotatingFileHandler

def setup_logger(log_dir):
    """Configura el sistema de logging"""
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Configuración del formato
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Logger para la aplicación
    app_logger = logging.getLogger('app')
    app_logger.setLevel(logging.INFO)
    
    # Handler para archivo de log con rotación
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, 'app.log'),
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    file_handler.setFormatter(formatter)
    
    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Agregar handlers al logger
    app_logger.addHandler(file_handler)
    app_logger.addHandler(console_handler)
    
    # Logger para scrapers
    scraper_logger = logging.getLogger('scraper')
    scraper_logger.setLevel(logging.INFO)
    
    # Handler para archivo de log del scraper
    scraper_file_handler = RotatingFileHandler(
        os.path.join(log_dir, 'scraper.log'),
        maxBytes=10485760,
        backupCount=10
    )
    scraper_file_handler.setFormatter(formatter)
    scraper_logger.addHandler(scraper_file_handler)
    scraper_logger.addHandler(console_handler)
    
    return app_logger, scraper_logger