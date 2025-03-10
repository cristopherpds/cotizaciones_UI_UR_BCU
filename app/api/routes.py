from flask import Blueprint, jsonify, request
from app.api.controllers import CotizacionController

api_bp = Blueprint('api', __name__)
@api_bp.route('/health', methods=['GET'])
def health_check():
    """Endpoint para verificar que la API está funcionando"""
    return jsonify({
        'status': 'ok',
        'version': '1.0.0'
    })

@api_bp.route('/info', methods=['GET'])
def get_api_info():
    """Endpoint con información sobre la API"""
    return jsonify({
        'nombre': 'API de Cotizaciones BCU (Unidad Indexada y Reajustable)',
        'descripcion': 'API para obtener cotizaciones de UI y UR desde el Banco Central del Uruguay',
        'endpoints': [
            {
                'ruta': '/api/cotizacion/ui',
                'metodo': 'GET',
                'descripcion': 'Obtiene la cotización de la Unidad Indexada para una fecha específica',
                'parametros': ['fecha (opcional, formato YYYY-MM-DD, por defecto usa la fecha actual)'],
                'ejemplo': '/api/cotizacion/ui?fecha=2023-12-31',
                'respuesta': {
                    'tipo': 'UI',
                    'moneda': 'UNIDAD INDEXADA',
                    'fecha': '2023-12-31',
                    'valor': 5.8642
                }
            },
            {
                'ruta': '/api/cotizacion/ur',
                'metodo': 'GET',
                'descripcion': 'Obtiene la cotización de la Unidad Reajustable para una fecha específica',
                'parametros': ['fecha (opcional, formato YYYY-MM-DD, por defecto usa la fecha actual)'],
                'ejemplo': '/api/cotizacion/ur?fecha=2023-12-31',
                'respuesta': {
                    'tipo': 'UR',
                    'moneda': 'UNIDAD REAJUSTABLE',
                    'fecha': '2023-12-31',
                    'valor': 1532.33
                }
            },
            {
                'ruta': '/api/historico/ui',
                'metodo': 'GET',
                'descripcion': 'Obtiene datos históricos de la Unidad Indexada en un rango de fechas',
                'parametros': [
                    'inicio (opcional, formato YYYY-MM-DD)',
                    'fin (opcional, formato YYYY-MM-DD)'
                ],
                'ejemplo': '/api/historico/ui?inicio=2023-01-01&fin=2023-01-31',
                'nota': 'Este endpoint actualmente depende del método get_ui_historico que debe implementarse en el BaseScraper'
            },
            {
                'ruta': '/api/historico/ur',
                'metodo': 'GET',
                'descripcion': 'Obtiene datos históricos de la Unidad Reajustable en un rango de fechas',
                'parametros': [
                    'inicio (opcional, formato YYYY-MM-DD)',
                    'fin (opcional, formato YYYY-MM-DD)'
                ],
                'ejemplo': '/api/historico/ur?inicio=2023-01-01&fin=2023-01-31',
                'nota': 'Este endpoint actualmente depende del método get_ur_historico que debe implementarse en el BaseScraper'
            }
        ],
        'características': [
            'Datos obtenidos directamente desde el Banco Central del Uruguay',
            'Sistema de caché para evitar consultas repetidas y mejorar rendimiento',
            'Logs detallados para seguimiento de operaciones y errores'
        ],
        'version': '1.0.0',
        'autor': 'Sistema de Cotizaciones BCU'
    })

@api_bp.route('/cotizacion/<tipo_unidad>', methods=['GET'])
def get_cotizacion(tipo_unidad):
    """Endpoint para obtener la cotización de una unidad"""
    fecha = request.args.get('fecha', None)
    
    controller = CotizacionController()
    result = controller.get_cotizacion(tipo_unidad.lower(), fecha)
    
    if 'error' in result:
        return jsonify(result), 400
    
    return jsonify(result)

@api_bp.route('/historico/<tipo_unidad>', methods=['GET'])
def get_historico(tipo_unidad):
    """
    Endpoint para obtener datos históricos de una unidad monetaria (UI o UR)
    
    Parámetros de URL:
    - tipo_unidad: 'ui' para Unidad Indexada, 'ur' para Unidad Reajustable
    
    Parámetros de consulta (Query Parameters):
    - inicio: (opcional) Fecha inicial en formato YYYY-MM-DD
    - fin: (opcional) Fecha final en formato YYYY-MM-DD
    
    Si no se proporcionan fechas:
    - fecha_fin: se usa la fecha actual
    - fecha_inicio: se usa 30 días antes de fecha_fin
    
    Respuesta exitosa:
    {
        "tipo": "UI/UR",
        "moneda": "UNIDAD INDEXADA/UNIDAD REAJUSTABLE",
        "fecha_inicio": "YYYY-MM-DD",
        "fecha_fin": "YYYY-MM-DD",
        "cotizaciones": [
            {
                "tipo": "UI/UR",
                "moneda": "UNIDAD INDEXADA/UNIDAD REAJUSTABLE",
                "fecha": "YYYY-MM-DD",
                "valor": 123.45
            }
        ],
        "metadata": {
            "total_registros": 30,
            "dias_solicitados": 30,
            "fuente": "Banco Central del Uruguay"
        }
    }
    
    Respuesta de error:
    {
        "error": "Descripción del error",
        "codigo": "CODIGO_ERROR"
    }
    
    Códigos de error:
    - INVALID_UNIT_TYPE: Tipo de unidad inválido
    - INVALID_DATE_FORMAT: Formato de fecha inválido
    - INVALID_DATE_RANGE: Rango de fechas inválido
    - DATE_RANGE_TOO_LARGE: Rango mayor a 365 días
    - DATA_FETCH_ERROR: Error al obtener datos del BCU
    - SCRAPER_ERROR: Error en el proceso de extracción
    - GENERAL_ERROR: Error general del sistema
    """
    fecha_inicio = request.args.get('inicio', None)
    fecha_fin = request.args.get('fin', None)
    
    controller = CotizacionController()
    result = controller.get_historico(tipo_unidad.lower(), fecha_inicio, fecha_fin)
    
    if 'error' in result:
        return jsonify(result), 400
    
    return jsonify(result)