# Script de prueba rápida para Numa
# Ejecutar desde la carpeta tests/ mientras el servidor está corriendo
# Uso: cd tests && .\test_system.ps1

Write-Host "=== PRUEBA NUMA - FLUJO COMPLETO ===" -ForegroundColor Green
Write-Host ""

# 1. Crear transacción por voz
Write-Host "1. Creando transacción por voz..." -ForegroundColor Yellow
$response1 = curl.exe -X POST "http://localhost:8000/upload-audio" `
  -H "Content-Type: multipart/form-data" `
  -F "audio_file=@audio_dummy.mp3" `
  -F "user_id=1"

Write-Host "Respuesta:" -ForegroundColor Cyan
$response1
Write-Host ""

# 2. Verificar con documento
Write-Host "2. Verificando con documento..." -ForegroundColor Yellow
$response2 = curl.exe -X POST "http://localhost:8000/upload-document" `
  -H "Content-Type: multipart/form-data" `
  -F "document=@recibo_starbucks.jpg" `
  -F "transaction_id=1"

Write-Host "Respuesta:" -ForegroundColor Cyan
$response2
Write-Host ""

# 3. Consultar gastos via chat
Write-Host "3. Consultando gastos hoy..." -ForegroundColor Yellow
$response3 = curl.exe -X POST "http://localhost:8000/chat" `
  -H "Content-Type: application/json" `
  -d '{\"message\": \"¿Cuánto gasté hoy?\", \"user_id\": 1}'

Write-Host "Respuesta:" -ForegroundColor Cyan
$response3
Write-Host ""

# 4. Consultar por categoría
Write-Host "4. Consultando gastos en alimentación..." -ForegroundColor Yellow
$response4 = curl.exe -X POST "http://localhost:8000/chat" `
  -H "Content-Type: application/json" `
  -d '{\"message\": \"¿Cuánto gasté en alimentación?\", \"user_id\": 1}'

Write-Host "Respuesta:" -ForegroundColor Cyan
$response4
Write-Host ""

Write-Host "=== PRUEBA COMPLETADA ===" -ForegroundColor Green
Write-Host "Ve a http://localhost:8000/docs para la interfaz web interactiva" -ForegroundColor Blue