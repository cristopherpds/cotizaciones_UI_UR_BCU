from flask import Blueprint, jsonify

swagger_bp = Blueprint('swagger', __name__)

@swagger_bp.route('/swagger.json', methods=['GET'])
def swagger_json():
    """Generate Swagger JSON specification"""
    swagger_spec = {
        "swagger": "2.0",
        "info": {
            "title": "BCU Exchange Rate API",
            "description": "API for retrieving UI and UR values from the Central Bank of Uruguay",
            "version": "1.0.0"
        },
        "basePath": "/api",  # Base path is already correctly set to /api
        "schemes": ["http", "https"],
        "paths": {
            "/health": {
                "get": {
                    "summary": "Health check endpoint",
                    "description": "Verify that the API is operational",
                    "produces": ["application/json"],
                    "responses": {
                        "200": {
                            "description": "API is operational",
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "status": {"type": "string", "example": "ok"},
                                    "version": {"type": "string", "example": "1.0.0"}
                                }
                            }
                        }
                    },
                    "tags": ["System"]
                }
            },
            "/info": {
                "get": {
                    "summary": "API information",
                    "description": "Get detailed information about available endpoints",
                    "produces": ["application/json"],
                    "responses": {
                        "200": {
                            "description": "API information returned successfully",
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "nombre": {"type": "string"},
                                    "descripcion": {"type": "string"},
                                    "endpoints": {"type": "array"},
                                    "características": {"type": "array"},
                                    "version": {"type": "string"}
                                }
                            }
                        }
                    },
                    "tags": ["System"]
                }
            },
            "/cotizacion/{tipo_unidad}": {
                "get": {
                    "summary": "Get quotation",
                    "description": "Get the quotation for UI or UR for a specific date",
                    "produces": ["application/json"],
                    "parameters": [
                        {
                            "name": "tipo_unidad",
                            "in": "path",
                            "required": True,
                            "type": "string",
                            "enum": ["ui", "ur"],
                            "description": "Type of unit (UI or UR)"
                        },
                        {
                            "name": "fecha",
                            "in": "query",
                            "required": False,
                            "type": "string",
                            "format": "date",
                            "description": "Date in YYYY-MM-DD format. Defaults to current date if not provided"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Quotation returned successfully",
                            "schema": {
                                "$ref": "#/definitions/CotizacionResponse"
                            }
                        },
                        "400": {
                            "description": "Bad request",
                            "schema": {
                                "$ref": "#/definitions/ErrorResponse"
                            }
                        }
                    },
                    "tags": ["Quotations"]
                }
            },
            "/historico/{tipo_unidad}": {
                "get": {
                    "summary": "Get historical data",
                    "description": "Get historical values for UI or UR in a date range",
                    "produces": ["application/json"],
                    "parameters": [
                        {
                            "name": "tipo_unidad",
                            "in": "path",
                            "required": True,
                            "type": "string",
                            "enum": ["ui", "ur"],
                            "description": "Type of unit (UI or UR)"
                        },
                        {
                            "name": "inicio",
                            "in": "query",
                            "required": False,
                            "type": "string",
                            "format": "date",
                            "description": "Start date in YYYY-MM-DD format"
                        },
                        {
                            "name": "fin",
                            "in": "query",
                            "required": False,
                            "type": "string",
                            "format": "date",
                            "description": "End date in YYYY-MM-DD format"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Historical data returned successfully",
                            "schema": {
                                "$ref": "#/definitions/HistoricoResponse"
                            }
                        },
                        "400": {
                            "description": "Bad request",
                            "schema": {
                                "$ref": "#/definitions/ErrorResponse"
                            }
                        }
                    },
                    "tags": ["Quotations"]
                }
            }
        },
        "definitions": {
            "Cotizacion": {
                "type": "object",
                "properties": {
                    "tipo": {"type": "string", "example": "UI"},
                    "moneda": {"type": "string", "example": "UNIDAD INDEXADA"},
                    "fecha": {"type": "string", "example": "2023-12-31"},
                    "valor": {"type": "number", "example": 5.8642}
                }
            },
            "CotizacionResponse": {
                "type": "object",
                "properties": {
                    "tipo": {"type": "string", "example": "UI"},
                    "moneda": {"type": "string", "example": "UNIDAD INDEXADA"},
                    "fecha": {"type": "string", "example": "2023-12-31"},
                    "valor": {"type": "number", "example": 5.8642},
                    "metadata": {
                        "type": "object",
                        "properties": {
                            "fuente": {"type": "string", "example": "Banco Central del Uruguay"},
                            "fecha_consulta": {"type": "string", "example": "2023-12-31 15:30:45"}
                        }
                    }
                }
            },
            "HistoricoResponse": {
                "type": "object",
                "properties": {
                    "tipo": {"type": "string", "example": "UI"},
                    "moneda": {"type": "string", "example": "UNIDAD INDEXADA"},
                    "fecha_inicio": {"type": "string", "example": "2023-01-01"},
                    "fecha_fin": {"type": "string", "example": "2023-01-31"},
                    "cotizaciones": {
                        "type": "array",
                        "items": {
                            "$ref": "#/definitions/Cotizacion"
                        }
                    },
                    "metadata": {
                        "type": "object",
                        "properties": {
                            "total_registros": {"type": "integer", "example": 31},
                            "dias_solicitados": {"type": "integer", "example": 31},
                            "fuente": {"type": "string", "example": "Banco Central del Uruguay"}
                        }
                    }
                }
            },
            "ErrorResponse": {
                "type": "object",
                "properties": {
                    "error": {"type": "string", "example": "Descripción del error"},
                    "codigo": {"type": "string", "example": "ERROR_CODE"}
                }
            }
        },
        "tags": [
            {
                "name": "System",
                "description": "System and diagnostic endpoints"
            },
            {
                "name": "Quotations",
                "description": "Access to UI and UR quotation data"
            }
        ]
    }
    
    return jsonify(swagger_spec)