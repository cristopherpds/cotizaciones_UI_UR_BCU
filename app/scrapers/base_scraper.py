# app/scrapers/base_scraper.py
import requests
import random
import time
import datetime
import logging
from bs4 import BeautifulSoup

logger = logging.getLogger('scraper.base')

class BaseScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def get(self, url, params=None, retry_count=3):
        """
        Realiza una petición GET con reintentos
        
        Args:
            url (str): URL a la que hacer la petición
            params (dict, optional): Parámetros de la URL
            retry_count (int): Número de reintentos en caso de error
            
        Returns:
            Response: Respuesta de la petición o None si falló
        """
        for i in range(retry_count):
            try:
                # Añadimos verify=False para ignorar la verificación del certificado SSL
                # Esto es necesario porque el certificado del BCU puede no estar en el bundle por defecto
                response = self.session.get(url, params=params, timeout=10, verify=False)
                
                # Silenciamos las advertencias de las solicitudes no verificadas
                requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
                
                if response.status_code == 200:
                    return response
                
                logger.warning(f"Intento {i+1}/{retry_count} fallido: Status code {response.status_code}")
                time.sleep(random.uniform(1, 3))  # Espera aleatoria entre intentos
            except Exception as e:
                logger.error(f"Error en petición GET: {str(e)}")
                time.sleep(random.uniform(1, 3))  # Espera aleatoria entre intentos
                
        return None

    def parse_html(self, html_content):
        """
        Analiza contenido HTML con BeautifulSoup
        
        Args:
            html_content (str): Contenido HTML a analizar
            
        Returns:
            BeautifulSoup: Objeto para navegar y buscar en el HTML
        """
        return BeautifulSoup(html_content, 'html.parser')
        
    def get_ui_cotizacion(self, fecha):
        """
        Obtiene la cotización de la Unidad Indexada para una fecha específica
        
        Args:
            fecha (str): Fecha en formato YYYY-MM-DD
            
        Returns:
            dict: Diccionario con la cotización o mensaje de error
        """
        try:
            # URL correcta para la cotización de UI
            url = "https://www.bcu.gub.uy/Estadisticas-e-Indicadores/Paginas/Cotizaciones.aspx"
            
            # Convertir la fecha al formato adecuado para la solicitud
            fecha_obj = datetime.datetime.strptime(fecha, "%Y-%m-%d")
            fecha_formateada = fecha_obj.strftime("%d/%m/%Y")
            
            # Realizar la solicitud para obtener la información
            params = {
                "fecha": fecha_formateada,
                "tipo": "ui"
            }
            
            response = self.get(url, params=params)
            if not response:
                return {"error": "No se pudo conectar con el servidor del BCU"}
                
            # Analizar el HTML para encontrar el valor de la UI
            soup = self.parse_html(response.text)
            
            # Buscar la tabla con los datos de cotización
            tabla_cotizacion = soup.select_one("table.resultado")
            
            if not tabla_cotizacion:
                return {"error": "No se encontró la tabla de cotizaciones en la página"}
                
            # Buscar la fila que contiene "UNIDAD INDEXADA"
            valor_ui = None
            moneda_nombre = None
            for fila in tabla_cotizacion.select("tr"):
                celdas = fila.select("td")
                if len(celdas) >= 3:  # Asegurarse de que hay suficientes columnas
                    moneda = celdas[0].text.strip()
                    if "UNIDAD INDEXADA" in moneda:
                        moneda_nombre = moneda
                        # El valor está en la columna de venta (o compra, son iguales para UI)
                        valor_texto = celdas[2].text.strip()  # Columna "Venta"
                        valor_texto = valor_texto.replace(".", "").replace(",", ".")
                        valor_ui = float(valor_texto)
                        break
            
            if valor_ui is None:
                # Si no se encuentra en la tabla principal, buscar de forma más genérica
                texto_pagina = soup.get_text()
                import re
                match = re.search(r'(UNIDAD INDEXADA)[^0-9,]*([0-9]+,[0-9]+)', texto_pagina, re.IGNORECASE)
                if match:
                    moneda_nombre = match.group(1)
                    valor_texto = match.group(2).replace(".", "").replace(",", ".")
                    valor_ui = float(valor_texto)
            
            if valor_ui is None:
                return {"error": "No se pudo encontrar el valor de la Unidad Indexada"}
                
            return {
                "tipo": "UI",
                "moneda": moneda_nombre or "UNIDAD INDEXADA",
                "fecha": fecha,
                "valor": valor_ui
            }
            
        except Exception as e:
            import traceback
            return {"error": f"Error al obtener cotización UI: {str(e)}", "traceback": traceback.format_exc()}
                    
    def get_ur_cotizacion(self, fecha):
        """
        Obtiene la cotización de la Unidad Reajustable para una fecha específica
        
        Args:
            fecha (str): Fecha en formato YYYY-MM-DD
            
        Returns:
            dict: Diccionario con la cotización o mensaje de error
        """
        try:
            # URL correcta para la cotización de UR
            url = "https://www.bcu.gub.uy/Estadisticas-e-Indicadores/Paginas/Cotizaciones.aspx"
            
            # Convertir la fecha al formato adecuado para la solicitud
            fecha_obj = datetime.datetime.strptime(fecha, "%Y-%m-%d")
            fecha_formateada = fecha_obj.strftime("%d/%m/%Y")
            
            # Realizar la solicitud para obtener la información
            params = {
                "fecha": fecha_formateada,
                "tipo": "ur"  # Mantener este parámetro aunque la página maneja todas las monedas juntas
            }
            
            response = self.get(url, params=params)
            if not response:
                return {"error": "No se pudo conectar con el servidor del BCU"}
                    
            soup = self.parse_html(response.text)
            
            # Buscar la tabla con los datos de cotización
            tabla_cotizacion = soup.select_one("table.resultado")
            
            if not tabla_cotizacion:
                return {"error": "No se encontró la tabla de cotizaciones en la página"}
                
            # Buscar la fila que contiene "UNIDAD REAJUSTAB"
            valor_ur = None
            moneda_nombre = None
            for fila in tabla_cotizacion.select("tr"):
                celdas = fila.select("td")
                if len(celdas) >= 3:  # Asegurarse de que hay suficientes columnas
                    moneda = celdas[0].text.strip()
                    if "UNIDAD REAJUSTAB" in moneda:
                        moneda_nombre = moneda
                        # El valor está en la columna de venta (o compra, son iguales)
                        valor_texto = celdas[2].text.strip()  # Columna "Venta"
                        valor_texto = valor_texto.replace(".", "").replace(",", ".")
                        valor_ur = float(valor_texto)
                        break
            
            if valor_ur is None:
                # Si no se encuentra en la tabla principal, buscar de forma más genérica
                texto_pagina = soup.get_text()
                import re
                match = re.search(r'(UNIDAD REAJUSTAB[^:]*)[^0-9,]*([0-9]+,[0-9]+)', texto_pagina, re.IGNORECASE)
                if match:
                    moneda_nombre = match.group(1)
                    valor_texto = match.group(2).replace(".", "").replace(",", ".")
                    valor_ur = float(valor_texto)
            
            if valor_ur is None:
                return {"error": "No se pudo encontrar el valor de la Unidad Reajustable"}
                
            return {
                "tipo": "UR",
                "moneda": moneda_nombre or "UNIDAD REAJUSTABLE",
                "fecha": fecha,
                "valor": valor_ur
            }
                
        except Exception as e:
            import traceback
            return {"error": f"Error al obtener cotización UR: {str(e)}", "traceback": traceback.format_exc()}

    def get_ui_historico(self, fecha_inicio=None, fecha_fin=None):
        """
        Obtiene datos históricos de la Unidad Indexada para un rango de fechas
        
        Args:
            fecha_inicio (str, optional): Fecha inicial en formato YYYY-MM-DD
            fecha_fin (str, optional): Fecha final en formato YYYY-MM-DD
            
        Returns:
            dict: Diccionario con los datos históricos o mensaje de error
        """
        try:
            # Si no se proporcionan fechas, usar últimos 30 días
            if not fecha_inicio:
                fecha_fin_obj = datetime.datetime.now()
                fecha_inicio_obj = fecha_fin_obj - datetime.timedelta(days=30)
                fecha_inicio = fecha_inicio_obj.strftime('%Y-%m-%d')
            
            if not fecha_fin:
                fecha_fin = datetime.datetime.now().strftime('%Y-%m-%d')
            
            # Convertir fechas a objetos datetime para validación
            fecha_inicio_obj = datetime.datetime.strptime(fecha_inicio, '%Y-%m-%d')
            fecha_fin_obj = datetime.datetime.strptime(fecha_fin, '%Y-%m-%d')
            
            # Validar que fecha_inicio no sea posterior a fecha_fin
            if fecha_inicio_obj > fecha_fin_obj:
                return {'error': 'La fecha de inicio no puede ser posterior a la fecha final'}
            
            # Validar que el rango no sea mayor a 365 días
            dias_diferencia = (fecha_fin_obj - fecha_inicio_obj).days
            if dias_diferencia > 365:
                return {'error': 'El rango de fechas no puede ser mayor a 365 días'}
            
            # Obtener cotizaciones para cada fecha
            cotizaciones = []
            fecha_actual = fecha_inicio_obj
            while fecha_actual <= fecha_fin_obj:
                fecha_str = fecha_actual.strftime('%Y-%m-%d')
                resultado = self.get_ui_cotizacion(fecha_str)
                
                if 'error' not in resultado:
                    cotizaciones.append(resultado)
                
                fecha_actual += datetime.timedelta(days=1)
                # Pequeña pausa para no sobrecargar el servidor
                time.sleep(random.uniform(0.5, 1))
            
            if not cotizaciones:
                return {'error': 'No se encontraron cotizaciones para el rango de fechas especificado'}
            
            return {
                'tipo': 'UI',
                'moneda': 'UNIDAD INDEXADA',
                'fecha_inicio': fecha_inicio,
                'fecha_fin': fecha_fin,
                'cotizaciones': cotizaciones
            }
            
        except Exception as e:
            import traceback
            return {'error': f'Error al obtener datos históricos UI: {str(e)}', 'traceback': traceback.format_exc()}
    
    def get_ur_historico(self, fecha_inicio=None, fecha_fin=None):
        """
        Obtiene datos históricos de la Unidad Reajustable para un rango de fechas
        
        Args:
            fecha_inicio (str, optional): Fecha inicial en formato YYYY-MM-DD
            fecha_fin (str, optional): Fecha final en formato YYYY-MM-DD
            
        Returns:
            dict: Diccionario con los datos históricos o mensaje de error
        """
        try:
            # Si no se proporcionan fechas, usar últimos 30 días
            if not fecha_inicio:
                fecha_fin_obj = datetime.datetime.now()
                fecha_inicio_obj = fecha_fin_obj - datetime.timedelta(days=30)
                fecha_inicio = fecha_inicio_obj.strftime('%Y-%m-%d')
            
            if not fecha_fin:
                fecha_fin = datetime.datetime.now().strftime('%Y-%m-%d')
            
            # Convertir fechas a objetos datetime para validación
            fecha_inicio_obj = datetime.datetime.strptime(fecha_inicio, '%Y-%m-%d')
            fecha_fin_obj = datetime.datetime.strptime(fecha_fin, '%Y-%m-%d')
            
            # Validar que fecha_inicio no sea posterior a fecha_fin
            if fecha_inicio_obj > fecha_fin_obj:
                return {'error': 'La fecha de inicio no puede ser posterior a la fecha final'}
            
            # Validar que el rango no sea mayor a 365 días
            dias_diferencia = (fecha_fin_obj - fecha_inicio_obj).days
            if dias_diferencia > 365:
                return {'error': 'El rango de fechas no puede ser mayor a 365 días'}
            
            # Obtener cotizaciones para cada fecha
            cotizaciones = []
            fecha_actual = fecha_inicio_obj
            while fecha_actual <= fecha_fin_obj:
                fecha_str = fecha_actual.strftime('%Y-%m-%d')
                resultado = self.get_ur_cotizacion(fecha_str)
                
                if 'error' not in resultado:
                    cotizaciones.append(resultado)
                
                fecha_actual += datetime.timedelta(days=1)
                # Pequeña pausa para no sobrecargar el servidor
                time.sleep(random.uniform(0.5, 1))
            
            if not cotizaciones:
                return {'error': 'No se encontraron cotizaciones para el rango de fechas especificado'}
            
            return {
                'tipo': 'UR',
                'moneda': 'UNIDAD REAJUSTABLE',
                'fecha_inicio': fecha_inicio,
                'fecha_fin': fecha_fin,
                'cotizaciones': cotizaciones
            }
            
        except Exception as e:
            import traceback
            return {'error': f'Error al obtener datos históricos UR: {str(e)}', 'traceback': traceback.format_exc()}
