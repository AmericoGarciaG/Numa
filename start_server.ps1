# Script para iniciar el servidor Numa
# Ejecutar desde una terminal separada

Write-Host "🚀 Iniciando servidor Numa..." -ForegroundColor Green
Write-Host "Directorio actual: $PWD" -ForegroundColor Yellow
Write-Host ""

# Verificar que estamos en el directorio correcto
if (!(Test-Path "main.py")) {
    Write-Host "❌ Error: No se encuentra main.py en el directorio actual" -ForegroundColor Red
    Write-Host "   Asegúrate de estar en: C:\00_SW_Projects\01 Numa\Numa" -ForegroundColor Yellow
    exit 1
}

# Verificar entorno virtual
if (!(Test-Path "venv\Scripts\python.exe")) {
    Write-Host "⚠️  Advertencia: No se detectó entorno virtual" -ForegroundColor Yellow
    Write-Host "   Considera activar con: .\venv\Scripts\Activate.ps1" -ForegroundColor Yellow
}

Write-Host "✅ Archivos verificados" -ForegroundColor Green
Write-Host "🌐 El servidor estará disponible en: http://localhost:8000" -ForegroundColor Cyan
Write-Host "📚 Documentación interactiva en: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Para detener el servidor: Ctrl+C" -ForegroundColor Yellow
Write-Host "==================================================" -ForegroundColor Gray

# Iniciar el servidor
py -m uvicorn main:app --reload --host 0.0.0.0 --port 8000