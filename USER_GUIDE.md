# Numa - Guía de Usuario
## Asistente Financiero Personal

Esta guía te ayudará a probar todas las funcionalidades del sistema Numa como usuario final.

## Requisitos Previos

1. **Entorno Virtual Activado**:
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

2. **Dependencias Instaladas**:
   ```bash
   pip install -r requirements.txt
   ```

## Iniciar el Sistema

### Paso 1: Iniciar el Servidor
```bash
py -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

El servidor estará disponible en: http://localhost:8000

### Paso 2: Verificar que Funciona
Visita http://localhost:8000/docs para ver la documentación interactiva de la API.

## Flujo de Uso Completo

### 1. Crear Transacción por Voz (Simulada) 📢
**Endpoint**: `POST /upload-audio`

Simula el comando de voz: *"Pagué 15000 pesos en Starbucks por un café"*

```bash
# Usando curl (desde otra terminal)
curl -X POST "http://localhost:8000/upload-audio" \
  -H "Content-Type: multipart/form-data" \
  -F "audio_file=@tests/audio_dummy.mp3" \
  -F "user_id=1"
```

**Respuesta esperada**:
```json
{
  "transaction_id": 1,
  "status": "provisional",
  "message": "Audio procesado y transacción provisional creada",
  "extracted_data": {
    "amount": 15000,
    "concept": "café en Starbucks"
  }
}
```

### 2. Verificar con Comprobante 🧾
**Endpoint**: `POST /upload-document`

Sube un documento (imagen del recibo) para verificar la transacción:

```bash
curl -X POST "http://localhost:8000/upload-document" \
  -H "Content-Type: multipart/form-data" \
  -F "document=@tests/recibo_starbucks.jpg" \
  -F "transaction_id=1"
```

**Respuesta esperada**:
```json
{
  "transaction_id": 1,
  "status": "verified",
  "message": "Transacción verificada exitosamente",
  "verification_details": {
    "amount_verified": 15000,
    "merchant_verified": "Starbucks",
    "document_analysis": "Recibo válido confirmado por análisis multimodal"
  },
  "auto_categorized": {
    "category": "Alimentación",
    "reason": "Merchant conocido: Starbucks"
  }
}
```

### 3. Consultar Gastos por Chat 💬
**Endpoint**: `POST /chat`

Haz preguntas en lenguaje natural sobre tus gastos:

```bash
# ¿Cuánto gasté hoy?
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "¿Cuánto gasté hoy?", "user_id": 1}'
```

**Respuesta esperada**:
```json
{
  "response": "Hoy has gastado $15,000 en total. Tienes 1 transacción: $15,000 en Alimentación (Starbucks)."
}
```

## Ejemplos de Consultas de Chat

### Consultas por Período
```bash
# Esta semana
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "¿Cuánto gasté esta semana?", "user_id": 1}'

# Este mes
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "¿Cuánto gasté este mes?", "user_id": 1}'
```

### Consultas por Categoría
```bash
# Alimentación
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "¿Cuánto gasté en alimentación?", "user_id": 1}'

# Transporte
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "¿Cuánto gasté en transporte este mes?", "user_id": 1}'
```

## Usando la Interfaz Web Interactiva

### FastAPI Docs (Swagger UI)
1. Ve a: http://localhost:8000/docs
2. Expande cada endpoint para ver detalles
3. Haz clic en "Try it out" para probar directamente desde el navegador
4. Ingresa los parámetros necesarios
5. Haz clic en "Execute"

### Ejemplos de Archivos de Prueba

Puedes crear archivos dummy para probar:

```bash
# Los archivos de prueba ya están disponibles en tests/:
# tests/audio_dummy.mp3
# tests/recibo_starbucks.jpg

# Si necesitas recrearlos:
echo "dummy audio data" > tests/audio_dummy.mp3
echo "dummy receipt image" > tests/recibo_starbucks.jpg
```

## Flujo de Prueba Completo: Escenario Real

### Escenario: Compra en Supermarket y Uber

```bash
# 1. Primera transacción: Supermercado
curl -X POST "http://localhost:8000/upload-audio" \
  -H "Content-Type: multipart/form-data" \
  -F "audio_file=@audio1.mp3" \
  -F "user_id=1"

# 2. Verificar primera transacción
curl -X POST "http://localhost:8000/upload-document" \
  -H "Content-Type: multipart/form-data" \
  -F "document=@recibo_super.jpg" \
  -F "transaction_id=1"

# 3. Segunda transacción: Uber
curl -X POST "http://localhost:8000/upload-audio" \
  -H "Content-Type: multipart/form-data" \
  -F "audio_file=@audio2.mp3" \
  -F "user_id=1"

# 4. Verificar segunda transacción
curl -X POST "http://localhost:8000/upload-document" \
  -H "Content-Type: multipart/form-data" \
  -F "document=@recibo_uber.jpg" \
  -F "transaction_id=2"

# 5. Consultar gastos totales
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "¿Cuánto gasté hoy en total?", "user_id": 1}'

# 6. Consultar por categoría específica
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "¿Cuánto gasté en transporte?", "user_id": 1}'
```

## Troubleshooting

### Error de Conexión a Base de Datos
```bash
# Reiniciar servidor para recrear la base de datos
py -m uvicorn main:app --reload
```

### Error 422 (Validation Error)
- Verifica que los parámetros estén correctamente formateados
- Usa la interfaz web /docs para ver los esquemas exactos

### Ver Logs del Servidor
El servidor mostrará logs detallados en la terminal donde lo ejecutaste:
- Peticiones recibidas
- Procesamiento de transacciones
- Errores si los hay

## Datos de Prueba Incluidos

El sistema incluye:
- **Merchants conocidos**: Starbucks, McDonald's, Uber, etc.
- **Auto-categorización**: Alimentación, Transporte, Entretenimiento, etc.
- **Simulación de AI**: Para transcripción y análisis de documentos

## Próximos Pasos

Una vez que hayas probado todo el flujo:
1. ✅ Verifica que las transacciones se crean correctamente
2. ✅ Confirma que la verificación funciona
3. ✅ Prueba diferentes tipos de consultas de chat
4. ✅ Experimenta con múltiples transacciones
5. ✅ Testa la auto-categorización con diferentes merchants

¡Disfruta probando tu asistente financiero personal Numa! 🚀