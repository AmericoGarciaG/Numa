# 🚀 PRUEBA RÁPIDA DE NUMA - PASO A PASO

## Paso 1: Iniciar el Servidor

**En una nueva terminal PowerShell:**

```powershell
# Navegar al directorio del proyecto
cd "C:\00_SW_Projects\01 Numa\Numa"

# Opción A: Usar el script
.\start_server.ps1

# Opción B: Comando directo
py -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Verás algo así:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Application startup complete.
```

## Paso 2: Probar el Sistema

**⭐ OPCIÓN MÁS FÁCIL: Interfaz Web**

1. Ve a: **http://localhost:8000/docs**
2. Verás la interfaz Swagger UI
3. Prueba cada endpoint haciendo clic en "Try it out"

---

**📱 OPCIÓN AVANZADA: Comandos**

En **otra terminal PowerShell nueva**:

```powershell
# Navegar al mismo directorio
cd "C:\00_SW_Projects\01 Numa\Numa"

# Ejecutar el script de prueba
.\test_system.ps1
```

---

**🛠️ OPCIÓN MANUAL: Comandos Individuales**

En **otra terminal PowerShell nueva**:

```powershell
# 1. 🎤 Crear transacción por voz
curl.exe -X POST "http://localhost:8000/upload-audio" `
  -H "Content-Type: multipart/form-data" `
  -F "audio_file=@tests/audio_dummy.mp3" `
  -F "user_id=1"

# 2. 📄 Verificar con documento  
curl.exe -X POST "http://localhost:8000/upload-document" `
  -H "Content-Type: multipart/form-data" `
  -F "document=@tests/recibo_starbucks.jpg" `
  -F "transaction_id=1"

# 3. 💬 Consultar gastos
curl.exe -X POST "http://localhost:8000/chat" `
  -H "Content-Type: application/json" `
  -d "{\"message\": \"¿Cuánto gasté hoy?\", \"user_id\": 1}"
```

## ✅ Lo que Deberías Ver

### 1. Transacción por Voz
```json
{
  "id": 1,
  "amount": 15000,
  "concept": "café en Starbucks",
  "status": "provisional",
  "user_id": 1
}
```

### 2. Verificación con Documento
```json
{
  "id": 1,
  "amount": 15000,
  "concept": "café en Starbucks", 
  "status": "verified",
  "category": "Alimentación",
  "merchant": "Starbucks"
}
```

### 3. Consulta de Chat
```json
{
  "response": "Hoy has gastado $15,000 en total. Tienes 1 transacción: $15,000 en Alimentación (Starbucks)."
}
```

## 🔧 Solución de Problemas

### Error "Puerto en uso"
```powershell
# Cambiar puerto
py -m uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

### Error "curl no encontrado"
- Usar la interfaz web: http://localhost:8000/docs
- O instalar curl: `winget install curl`

### Error "archivos no encontrados"
```powershell
# Verificar archivos dummy
ls tests/audio_dummy.mp3, tests/recibo_starbucks.jpg
```

## 🎯 ¡Listo para Probar!

**Recomendación**: Empieza con la **interfaz web** (http://localhost:8000/docs) - es la forma más fácil de probar todos los endpoints sin comandos complicados.