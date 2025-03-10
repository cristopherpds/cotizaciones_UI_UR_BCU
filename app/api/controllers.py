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
            return {
                'error': f'Tipo de unidad inválido: {tipo_unidad}. Use "ui" o "ur"',
                'codigo': 'INVALID_UNIT_TYPE'
            }
        
        # Si no se proporciona fecha, usar la actual
        if fecha is None:
            fecha = datetime.datetime.now().strftime('%Y-%m-%d')
        else:
            # Validar formato de fecha
            try:
                datetime.datetime.strptime(fecha, '%Y-%m-%d')
            except ValueError:
                return {
                    'error': 'Formato de fecha inválido. Use YYYY-MM-DD',
                    'codigo': 'INVALID_DATE_FORMAT'
                }
        
        # Intentar obtener datos de la cache
        cache_key = f"{tipo_unidad}_{fecha}"
        cached_data = self.cache_service.get(cache_key)
        
        if cached_data:
            return cached_data
            
        # Si no está en cache, obtener datos del scraper
        try:
            if tipo_unidad == 'ui':
                data = self.scraper.get_ui_cotizacion(fecha)
                moneda_nombre = "UNIDAD INDEXADA"
            else:
                data = self.scraper.get_ur_cotizacion(fecha)
                moneda_nombre = "UNIDAD REAJUSTABLE"
                
            # Validar que se obtuvieron datos correctamente
            if 'error' in data:
                return {
                    'error': data['error'],
                    'codigo': 'DATA_FETCH_ERROR'
                }
            
            # Formatear respuesta con metadatos
            response = {
                'tipo': data['tipo'],
                'moneda': data['moneda'],
                'fecha': fecha,
                'valor': data['valor'],
                'metadata': {
                    'fuente': 'Banco Central del Uruguay',
                    'fecha_consulta': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            }
            
            # Añadir campos adicionales si existen en la respuesta del scraper
            for campo in ['valor_compra', 'valor_venta', 'valor_arbitraje']:
                if campo in data:
                    response[campo.replace('valor_', '')] = data[campo]
            
            # Guardar en cache si se obtuvo correctamente
            self.cache_service.set(cache_key, response)
            
            return response
        except Exception as e:
            return {
                'error': f'Error al obtener datos: {str(e)}',
                'codigo': 'SCRAPER_ERROR'
            }
    

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
            return {
                'error': f'Tipo de unidad inválido: {tipo_unidad}. Use "ui" o "ur"',
                'codigo': 'INVALID_UNIT_TYPE'
            }
        
        try:
            # Si no se proporciona fecha_fin, usar la fecha actual
            if not fecha_fin:
                fecha_fin = datetime.datetime.now().strftime('%Y-%m-%d')
            else:
                # Validar formato de fecha_fin
                try:
                    datetime.datetime.strptime(fecha_fin, '%Y-%m-%d')
                except ValueError:
                    return {
                        'error': 'Formato de fecha final inválido. Use YYYY-MM-DD',
                        'codigo': 'INVALID_DATE_FORMAT'
                    }
            
            # Si no se proporciona fecha_inicio, usar 30 días antes de fecha_fin
            if not fecha_inicio:
                fecha_fin_obj = datetime.datetime.strptime(fecha_fin, '%Y-%m-%d')
                fecha_inicio_obj = fecha_fin_obj - datetime.timedelta(days=30)
                fecha_inicio = fecha_inicio_obj.strftime('%Y-%m-%d')
            else:
                # Validar formato de fecha_inicio
                try:
                    datetime.datetime.strptime(fecha_inicio, '%Y-%m-%d')
                except ValueError:
                    return {
                        'error': 'Formato de fecha inicial inválido. Use YYYY-MM-DD',
                        'codigo': 'INVALID_DATE_FORMAT'
                    }
            
            # Validar rango de fechas
            fecha_inicio_obj = datetime.datetime.strptime(fecha_inicio, '%Y-%m-%d')
            fecha_fin_obj = datetime.datetime.strptime(fecha_fin, '%Y-%m-%d')
            
            if fecha_inicio_obj > fecha_fin_obj:
                return {
                    'error': 'La fecha de inicio no puede ser posterior a la fecha final',
                    'codigo': 'INVALID_DATE_RANGE'
                }
            
            dias_diferencia = (fecha_fin_obj - fecha_inicio_obj).days
            if dias_diferencia > 365:
                return {
                    'error': 'El rango de fechas no puede ser mayor a 365 días',
                    'codigo': 'DATE_RANGE_TOO_LARGE'
                }
            
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
                
                # Validar que se obtuvieron datos
                if 'error' in data:
                    return {
                        'error': data['error'],
                        'codigo': 'DATA_FETCH_ERROR'
                    }
                
                # Formatear respuesta según documentación
                response = {
                    'tipo': data['tipo'],
                    'moneda': data['moneda'],
                    'fecha_inicio': fecha_inicio,
                    'fecha_fin': fecha_fin,
                    'cotizaciones': data['cotizaciones'],
                    'metadata': {
                        'total_registros': len(data['cotizaciones']),
                        'dias_solicitados': dias_diferencia + 1,
                        'fuente': 'Banco Central del Uruguay'
                    }
                }
                
                # Guardar en cache
                self.cache_service.set(cache_key, response)
                return response
                
            except Exception as e:
                return {
                    'error': f'Error al obtener datos históricos: {str(e)}',
                    'codigo': 'SCRAPER_ERROR'
                }
                
        except Exception as e:
            return {
                'error': f'Error al procesar la solicitud: {str(e)}',
                'codigo': 'GENERAL_ERROR'
            }