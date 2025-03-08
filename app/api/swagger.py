from flask import Blueprint, jsonify

swagger_bp = Blueprint('swagger', __name__)

@swagger_bp.route('/swagger.json')
def swagger_json():
    """Generate Swagger JSON specification"""
    swagger_spec = {
        "swagger": "2.0",
        "info": {
            "title": "BCU Exchange Rate API",
            "description": "API for retrieving UI and UR values from the Central Bank of Uruguay",
            "version": "1.0.0"
        },
        "basePath": "/api",
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
                    }
                }
            },
            "/info": {
                "get": {
                    "summary": "API information",
                    "description": "Get detailed information about available endpoints",
                    "produces": ["application/json"],
                    "responses": {
                        "200": {
                            "description": "API information returned successfully"
                        }
                    }
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
                                "type": "object",
                                "properties": {
                                    "tipo": {"type": "string", "example": "UI"},
                                    "moneda": {"type": "string", "example": "UNIDAD INDEXADA"},
                                    "fecha": {"type": "string", "example": "2023-12-31"},
                                    "valor": {"type": "number", "example": 5.8642}
                                }
                            }
                        },
                        "400": {
                            "description": "Bad request",
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "error": {"type": "string"}
                                }
                            }
                        }
                    }
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
                            "description": "Historical data returned successfully"
                        },
                        "400": {
                            "description": "Bad request",
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "error": {"type": "string"}
                                }
                            }
                        }
                    }
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
            }
        }
    }
    
    return jsonify(swagger_spec)