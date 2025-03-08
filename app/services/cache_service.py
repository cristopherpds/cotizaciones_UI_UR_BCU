import os
import json
from datetime import datetime
import logging

logger = logging.getLogger('app.cache')

class CacheService:
    def __init__(self, cache_dir, timeout=24*60*60):
        """
        Inicializa el servicio de caché
        
        Args:
            cache_dir (str): Directorio para almacenar datos en caché
            timeout (int): Tiempo de expiración en segundos (default: 24 horas)
        """
        self.cache_dir = cache_dir
        self.timeout = timeout
        os.makedirs(cache_dir, exist_ok=True)
    
    def get(self, key):
        """
        Obtiene un valor de la caché si existe y no ha expirado
        
        Args:
            key (str): Clave para identificar el valor en caché
            
        Returns:
            dict: Datos almacenados en caché o None si no existe o expiró
        """
        cache_file = os.path.join(self.cache_dir, f"{key}.json")
        
        if not os.path.exists(cache_file):
            return None
        
        # Verificar si el archivo ha expirado
        file_time = os.path.getmtime(cache_file)
        age_seconds = datetime.now().timestamp() - file_time
        
        if age_seconds > self.timeout:
            logger.info(f"Caché expirada para {key}")
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info(f"Datos obtenidos de caché: {key}")
                return data
        except Exception as e:
            logger.error(f"Error al leer caché {key}: {str(e)}")
            return None
    
    def set(self, key, data):
        """
        Almacena un valor en la caché
        
        Args:
            key (str): Clave para identificar el valor
            data (dict): Datos a almacenar
            
        Returns:
            bool: True si se guardó correctamente, False en caso contrario
        """
        cache_file = os.path.join(self.cache_dir, f"{key}.json")
        
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            logger.info(f"Datos guardados en caché: {key}")
            return True
        except Exception as e:
            logger.error(f"Error al guardar en caché {key}: {str(e)}")
            return False
    
    def delete(self, key):
        """Elimina un valor de la caché"""
        cache_file = os.path.join(self.cache_dir, f"{key}.json")
        
        if os.path.exists(cache_file):
            try:
                os.remove(cache_file)
                logger.info(f"Caché eliminada: {key}")
                return True
            except Exception as e:
                logger.error(f"Error al eliminar caché {key}: {str(e)}")
        
        return False
    
    def clear_expired(self):
        """Elimina todos los archivos de caché expirados"""
        count = 0
        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(self.cache_dir, filename)
                file_time = os.path.getmtime(file_path)
                age_seconds = datetime.now().timestamp() - file_time
                
                if age_seconds > self.timeout:
                    try:
                        os.remove(file_path)
                        count += 1
                    except Exception as e:
                        logger.error(f"Error al eliminar caché expirada {filename}: {str(e)}")
        
        logger.info(f"Se eliminaron {count} archivos de caché expirados")
        return count