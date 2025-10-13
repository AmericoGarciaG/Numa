# Tests Documentation

Este directorio contiene todas las pruebas para el proyecto Numa, siguiendo las directivas de testing especificadas en `AGENTS.md`.

## Estructura de Pruebas

```
tests/
├── __init__.py                    # Package initialization
├── test_services.py              # Unit tests for services.py functions
├── test_voice_endpoint.py        # Tests for voice transaction endpoint (Rule 2.1)
├── test_verification_endpoint.py # Tests for verification endpoint (Rule 2.2)
├── test_categorization.py        # Tests for auto-categorization (Rule 2.4)
├── test_e2e_flow.py              # End-to-end flow tests (Rules 2.1→2.2→2.4)
├── test_chat_endpoint.py         # Tests for chat endpoint (Rules 3.1 & 3.2)
├── test_chat_with_data.py        # Integration tests for chat with real data
├── test_system.ps1               # PowerShell script for system testing
└── README.md                     # This file
```

## Tipos de Pruebas

### 1. Pruebas Unitarias
- **`test_services.py`**: Base de datos aislada, cobertura completa de funciones de servicio
- **`test_voice_endpoint.py`**: Tests específicos del endpoint de voz (Rule 2.1)
- **`test_verification_endpoint.py`**: Tests del endpoint de verificación (Rule 2.2)
- **`test_categorization.py`**: Tests de auto-categorización (Rule 2.4)

### 2. Pruebas de Integración
- **`test_e2e_flow.py`**: Flujo completo voz → verificación → categorización
- **`test_chat_endpoint.py`**: Tests del sistema de chat (Rules 3.1 & 3.2)
- **`test_chat_with_data.py`**: Tests de chat con datos reales de transacciones

### 3. Pruebas de Sistema
- **`test_system.ps1`**: Script PowerShell para pruebas end-to-end con curl

## Ejecución de Pruebas

### Ejecutar todas las pruebas desde raíz
```bash
py -m pytest tests/ -v
```

### Ejecutar pruebas específicas por categoría
```bash
# Solo tests de servicios (unitarias)
py -m pytest tests/test_services.py -v

# Solo tests de endpoints
py -m pytest tests/test_voice_endpoint.py tests/test_verification_endpoint.py -v

# Solo tests de chat
py -m pytest tests/test_chat_endpoint.py tests/test_chat_with_data.py -v

# Solo test end-to-end
py -m pytest tests/test_e2e_flow.py -v
```

### Ejecutar script de sistema (requiere servidor activo)
```bash
# Desde la carpeta tests/
cd tests
.\test_system.ps1
```

### Ejecutar pruebas específicas
```bash
py -m pytest tests/test_services.py::TestCreateProvisionalTransactionFromAudio -v
```

### Ejecutar con cobertura (requiere pytest-cov)
```bash
py -m pytest tests/ --cov=services --cov-report=html
```

## Cobertura de Pruebas

### Funciones de Servicio Cubiertas:
- ✅ `create_provisional_transaction_from_audio`
  - Creación exitosa de transacción provisional
  - Extracción correcta de monto y concepto
  - Estado PROVISIONAL asignado correctamente

- ✅ `verify_transaction_with_document`
  - Verificación exitosa de transacción provisional
  - Cambio de estado a VERIFIED
  - Actualización de datos de verificación
  - Auto-categorización integrada
  - Manejo de errores (transacción no encontrada, ya verificada)

- ✅ `get_chat_response`
  - Consultas sin transacciones
  - Consultas con transacciones existentes
  - Detección de períodos (hoy, semana, mes)
  - Detección de categorías
  - Consultas por categoría específica

### Auto-Categorización:
- ✅ Categorización de merchants conocidos
- ✅ Integración en flujo de verificación

## Base de Datos de Prueba

Cada test utiliza una base de datos SQLite en memoria completamente aislada:
- No afecta la base de datos de desarrollo
- Datos limpios para cada test
- Ejecución rápida y confiable

## Fixtures de Prueba

- `test_db_session`: Base de datos SQLite en memoria
- `test_user`: Usuario de prueba creado automáticamente

## Cumplimiento con AGENTS.md

Estas pruebas cumplen con todas las directivas especificadas en `AGENTS.md`:
- ✅ Toda nueva función de lógica de negocio tiene pruebas unitarias correspondientes
- ✅ Base de datos de prueba aislada de desarrollo
- ✅ Uso de pytest como framework de testing
- ✅ Formateo con black y organización con isort
- ✅ Tests deben pasar antes de cualquier commit

## Comandos de Pre-Commit

Antes de hacer commit, siempre ejecutar desde la raíz del proyecto:
```bash
py -m black .
py -m isort .
py -m pytest tests/ -v
```

## Pruebas Manuales del Sistema

### Opción 1: Script PowerShell (desde tests/)
```bash
cd tests
.\test_system.ps1
```

### Opción 2: Interfaz web interactiva
1. Iniciar servidor: `py -m uvicorn main:app --reload`
2. Ir a: http://localhost:8000/docs
3. Probar endpoints interactivamente
