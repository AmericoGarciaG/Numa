# Script para iniciar el servidor Numa FastAPI
# Depurado para la nueva estructura del proyecto con modulo app/
# Ejecutar desde la raiz del proyecto: .\start_server.ps1

Write-Host "Iniciando servidor Numa..." -ForegroundColor Green
Write-Host "Directorio actual: $PWD" -ForegroundColor Yellow
Write-Host ""

# Verificar que estamos en el directorio correcto del proyecto
if (!(Test-Path "app\main.py")) {
    Write-Host "ERROR: No se encuentra app\main.py en el directorio actual" -ForegroundColor Red
    Write-Host "       Asegurate de estar en la raiz del proyecto Numa" -ForegroundColor Yellow
    Write-Host "       Estructura esperada: C:\...\Numa\app\main.py" -ForegroundColor Yellow
    exit 1
}

# Verificar archivo de requisitos
if (!(Test-Path "requirements.txt")) {
    Write-Host "ADVERTENCIA: No se encuentra requirements.txt" -ForegroundColor Yellow
}

# Verificar entorno virtual
if (Test-Path "venv\Scripts\python.exe") {
    Write-Host "Entorno virtual detectado: venv\" -ForegroundColor Green
} elseif (Test-Path ".venv\Scripts\python.exe") {
    Write-Host "Entorno virtual detectado: .venv\" -ForegroundColor Green
} else {
    Write-Host "ADVERTENCIA: No se detecto entorno virtual" -ForegroundColor Yellow
    Write-Host "             Para mejor rendimiento, considera activar con:" -ForegroundColor Yellow
    Write-Host "             • .\venv\Scripts\Activate.ps1 (si tienes .venv)" -ForegroundColor Yellow
    Write-Host "             • .\venv\Scripts\Activate.ps1 (si tienes venv)" -ForegroundColor Yellow
}

# Verificar estructura del modulo app
Write-Host "Verificando estructura del modulo app..." -ForegroundColor Yellow
if (Test-Path "app\__init__.py") {
    Write-Host "Modulo app correctamente estructurado" -ForegroundColor Green
} else {
    Write-Host "ADVERTENCIA: Falta app\__init__.py" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Verificaciones completadas" -ForegroundColor Green
Write-Host "El servidor estara disponible en: http://localhost:8000" -ForegroundColor Cyan
Write-Host "Documentacion interactiva en: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "Modo desarrollo con recarga automatica habilitado" -ForegroundColor Cyan
Write-Host ""
Write-Host "Para detener el servidor: Ctrl+C" -ForegroundColor Yellow
Write-Host "=====================================================" -ForegroundColor Gray
Write-Host ""

# Iniciar el servidor con la nueva estructura del modulo app
try {
    python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
} catch {
    Write-Host "ERROR: No se pudo iniciar el servidor" -ForegroundColor Red
    Write-Host "       Verifica que tienes uvicorn instalado: pip install uvicorn[standard]" -ForegroundColor Yellow
    exit 1
}