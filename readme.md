# API de Cotizaciones BCU

Servicio API para obtener valores de "Unidad Indexada" (UI) y "Unidad Reajustable" (UR) desde el Banco Central del Uruguay (BCU).

## Descripción

Este servicio proporciona endpoints REST para consultar valores actuales e históricos de las unidades UI y UR, con un sistema de caché incorporado para mejorar el rendimiento y reducir la carga en el sitio web del BCU.

### ¿Qué son UI y UR?

- **UI (Unidad Indexada)**: Unidad de cuenta indexada utilizada en Uruguay vinculada al Índice de Precios al Consumo (IPC).
- **UR (Unidad Reajustable)**: Unidad ajustable utilizada en Uruguay para ciertas operaciones financieras y contratos.

## Comenzando

### Requisitos previos

- Python 3.9+
- Entorno virtual (recomendado)

### Instalación

1. Clonar el repositorio:

   ```bash
   git clone https://github.com/tuusuario/cotizaciones_UI_UR_BCU.git
   cd cotizaciones_UI_UR_BCU
   ```

2. Crear y activar un entorno virtual:

   ```bash
   python -m venv venv
   # En Windows
   venv\Scripts\activate
   # En Linux/Mac
   source venv/bin/activate
   ```

3. Instalar dependencias:

   ```bash
   pip install -r requirements.txt
   ```

4. Configurar entorno:

   ```bash
   # Copiar el archivo de ejemplo
   cp .env.example .env
   # Editar .env si es necesario
   ```

### Ejecutar la aplicación

Para desarrollo:

```bash
python run.py
```

Para producción:

```bash
gunicorn wsgi:application
```

## Documentación de la API

La API cuenta con documentación interactiva mediante Swagger UI, accesible en la ruta `/docs` una vez que la aplicación está en ejecución.

### Endpoints principales

#### Verificación de salud

```
GET /api/health
```

Comprobar si la API está funcionando correctamente.

**Respuesta:**

```json
{
  "status": "ok",
  "version": "1.0.0"
}
```

#### Información de la API

```
GET /api/info
```

Obtener información detallada sobre los endpoints disponibles.

#### Obtener cotización de UI

```
GET /api/cotizacion/ui?fecha=YYYY-MM-DD
```

Obtener el valor de la UI para una fecha específica (por defecto usa la fecha actual si no se proporciona).

**Ejemplo de solicitud:**

```
GET /api/cotizacion/ui?fecha=2023-12-31
```

**Ejemplo de respuesta:**

```json
{
  "tipo": "UI",
  "moneda": "UNIDAD INDEXADA",
  "fecha": "2023-12-31",
  "valor": 5.8642,
  "metadata": {
    "fuente": "Banco Central del Uruguay",
    "fecha_consulta": "2023-12-31 15:30:45"
  }
}
```

#### Obtener cotización de UR

```
GET /api/cotizacion/ur?fecha=YYYY-MM-DD
```

Obtener el valor de la UR para una fecha específica (por defecto usa la fecha actual si no se proporciona).

**Ejemplo de solicitud:**

```
GET /api/cotizacion/ur?fecha=2023-12-31
```

**Ejemplo de respuesta:**

```json
{
  "tipo": "UR",
  "moneda": "UNIDAD REAJUSTABLE",
  "fecha": "2023-12-31",
  "valor": 1532.33,
  "metadata": {
    "fuente": "Banco Central del Uruguay",
    "fecha_consulta": "2023-12-31 15:30:45"
  }
}
```

#### Obtener datos históricos de UI

```
GET /api/historico/ui?inicio=YYYY-MM-DD&fin=YYYY-MM-DD
```

Obtener valores históricos de UI para un rango de fechas.

**Ejemplo de solicitud:**

```
GET /api/historico/ui?inicio=2023-01-01&fin=2023-01-31
```

**Ejemplo de respuesta:**

```json
{
  "tipo": "UI",
  "moneda": "UNIDAD INDEXADA",
  "fecha_inicio": "2023-01-01",
  "fecha_fin": "2023-01-31",
  "cotizaciones": [
    {
      "tipo": "UI",
      "moneda": "UNIDAD INDEXADA",
      "fecha": "2023-01-01",
      "valor": 5.4321
    },
    {
      "tipo": "UI",
      "moneda": "UNIDAD INDEXADA",
      "fecha": "2023-01-02",
      "valor": 5.4325
    }
    // ... más cotizaciones
  ],
  "metadata": {
    "total_registros": 31,
    "dias_solicitados": 31,
    "fuente": "Banco Central del Uruguay"
  }
}
```

#### Obtener datos históricos de UR

```
GET /api/historico/ur?inicio=YYYY-MM-DD&fin=YYYY-MM-DD
```

Obtener valores históricos de UR para un rango de fechas.

**Ejemplo de solicitud:**

```
GET /api/historico/ur?inicio=2023-01-01&fin=2023-01-31
```

**Ejemplo de respuesta:**

```json
{
  "tipo": "UR",
  "moneda": "UNIDAD REAJUSTABLE",
  "fecha_inicio": "2023-01-01",
  "fecha_fin": "2023-01-31",
  "cotizaciones": [
    {
      "tipo": "UR",
      "moneda": "UNIDAD REAJUSTAB",
      "fecha": "2023-01-01",
      "valor": 1490.25
    },
    {
      "tipo": "UR",
      "moneda": "UNIDAD REAJUSTAB",
      "fecha": "2023-01-02",
      "valor": 1490.25
    }
    // ... más cotizaciones
  ],
  "metadata": {
    "total_registros": 31,
    "dias_solicitados": 31,
    "fuente": "Banco Central del Uruguay"
  }
}
```

## Características principales

- **Web Scraping**: Extrae datos directamente desde el sitio web del BCU
- **Sistema de caché**: Almacena datos obtenidos para minimizar peticiones y mejorar el rendimiento
- **Manejo de errores**: Sistema completo de manejo de errores y registro
- **Documentación de API**: Documentación interactiva con Swagger UI

## Sistema de caché

La API implementa un sistema de caché basado en archivos para mejorar el rendimiento:

- Los archivos de caché se almacenan en el directorio `cache`
- El tiempo de expiración predeterminado es de 24 horas (configurable)
- Las claves de caché se generan basadas en los parámetros de la solicitud

## Desarrollo

### Estructura del proyecto

```
├── app/                    # Paquete de la aplicación
│   ├── api/                # Endpoints de la API
│   ├── scrapers/           # Web scrapers para extracción de datos
│   ├── services/           # Capa de servicios
│   └── utils/              # Funciones de utilidad
├── cache/                  # Almacenamiento de caché
├── logs/                   # Registros de la aplicación
├── .env                    # Variables de entorno
├── .env.example            # Archivo de ejemplo de variables de entorno
├── requirements.txt        # Dependencias
├── run.py                  # Servidor de desarrollo
└── wsgi.py                 # Punto de entrada WSGI para producción
```

## Configuración de Swagger

La API incluye documentación interactiva mediante Swagger UI. Para acceder a la documentación:

1. Inicia la aplicación
2. Navega a `http://localhost:5000/docs`

La documentación te permite:

- Ver todos los endpoints disponibles
- Probar las solicitudes directamente desde el navegador
- Ver los esquemas de respuesta y formatos esperados

### Swagger JSON

La especificación Swagger está disponible en `/api/swagger.json` y contiene la siguiente estructura:

```json
{
  "swagger": "2.0",
  "info": {
    "title": "BCU Exchange Rate API",
    "description": "API for retrieving UI and UR values from the Central Bank of Uruguay",
    "version": "1.0.0"
  },
  "basePath": "/api",
  "schemes": ["http", "https"],
  "paths": {
    "/health": {...},
    "/info": {...},
    "/cotizacion/{tipo_unidad}": {...},
    "/historico/{tipo_unidad}": {...}
  }
}
```

## Contribuir

1. Haz un fork del repositorio
2. Crea tu rama de características (`git checkout -b feature/nueva-caracteristica`)
3. Haz commit de tus cambios (`git commit -m 'Añadir nueva característica'`)
4. Haz push a la rama (`git push origin feature/nueva-caracteristica`)
5. Abre un Pull Request

## Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.
