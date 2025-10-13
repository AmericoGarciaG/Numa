Write-Host "Iniciando servidor Numa..." -ForegroundColor Green
Write-Host "Servidor disponible en: http://localhost:8000" -ForegroundColor Cyan
Write-Host "Documentacion en: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""

py -m uvicorn main:app --reload --host 0.0.0.0 --port 8000