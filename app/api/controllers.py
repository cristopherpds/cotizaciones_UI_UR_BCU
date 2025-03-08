import datetime
import os
from flask import current_app
from app.services.cache_service import CacheService
from app.scrapers.base_scraper import BaseScraper

class CotizacionController:
    def __init__(self):
        # Get cache_dir from app config
        cache_dir = current_app.config['CACHE_DIR']
        self.cache_service = CacheService(cache_dir)
        self.scraper = BaseScraper()
    def get_cotizacion(self, tipo_unidad, fecha=None):
        """
        Obtiene la cotización de una unidad para una fecha específica
        
        Args:
            tipo_unidad (str): 'ui' para Unidad Indexada, 'ur' para Unidad Reajustable
            fecha (str, optional): Fecha en formato YYYY-MM-DD. Si es None, se usa la fecha actual.
        
        Returns:
            dict: Diccionario con la cotización o mensaje de error
        """
        # Validar tipo de unidad
        if tipo_unidad not in ['ui', 'ur']:
            return {'error': f'Tipo de unidad inválido: {tipo_unidad}. Use "ui" o "ur"'}
        
        # Si no se proporciona fecha, usar la actual
        if fecha is None:
            fecha = datetime.datetime.now().strftime('%Y-%m-%d')
        
        # Intentar obtener datos de la cache
        cache_key = f"{tipo_unidad}_{fecha}"
        cached_data = self.cache_service.get(cache_key)
        
        if cached_data:
            return cached_data
            
        # Si no está en cache, obtener datos del scraper
        try:
            if tipo_unidad == 'ui':
                data = self.scraper.get_ui_cotizacion(fecha)
            else:
                data = self.scraper.get_ur_cotizacion(fecha)
                
            # Guardar en cache si se obtuvo correctamente
            if 'error' not in data:
                self.cache_service.set(cache_key, data)
                
            return data
        except Exception as e:
            return {'error': f'Error al obtener datos: {str(e)}'}
    
    def get_historico(self, tipo_unidad, fecha_inicio=None, fecha_fin=None):
        """
        Obtiene datos históricos de una unidad para un rango de fechas
        
        Args:
            tipo_unidad (str): 'ui' para Unidad Indexada, 'ur' para Unidad Reajustable
            fecha_inicio (str, optional): Fecha inicial en formato YYYY-MM-DD
            fecha_fin (str, optional): Fecha final en formato YYYY-MM-DD
            
        Returns:
            dict: Diccionario con los datos históricos o mensaje de error
        """
        # Validar tipo de unidad
        if tipo_unidad not in ['ui', 'ur']:
            return {'error': f'Tipo de unidad inválido: {tipo_unidad}. Use "ui" o "ur"'}
        
        # Intentar obtener datos de la cache
        cache_key = f"historico_{tipo_unidad}_{fecha_inicio}_{fecha_fin}"
        cached_data = self.cache_service.get(cache_key)
        
        if cached_data:
            return cached_data
        
        # Si no está en cache, obtener datos del scraper
        try:
            if tipo_unidad == 'ui':
                data = self.scraper.get_ui_historico(fecha_inicio, fecha_fin)
            else:
                data = self.scraper.get_ur_historico(fecha_inicio, fecha_fin)
                
            # Guardar en cache si se obtuvo correctamente
            if 'error' not in data:
                self.cache_service.set(cache_key, data)
                
            return data
        except Exception as e:
            return {'error': f'Error al obtener datos históricos: {str(e)}'}