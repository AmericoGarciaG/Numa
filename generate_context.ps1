# Script para generar contexto completo del proyecto Numa con codificacion UTF-8
$OUTPUT_FILE = "CONTEXT.md"

Write-Host "Generando contexto del proyecto Numa..." -ForegroundColor Green
Remove-Item $OUTPUT_FILE -ErrorAction SilentlyContinue

# Encabezado
$header = @"
# Proyecto Numa - Contexto Completo

**Generado el:** $(Get-Date)
**Directorio:** $PWD

---

"@
$header | Out-File -FilePath $OUTPUT_FILE -Encoding utf8

# Estructura del proyecto
Write-Host "Generando estructura..." -ForegroundColor Yellow
"## Estructura del Proyecto" | Add-Content -Path $OUTPUT_FILE -Encoding utf8
"" | Add-Content -Path $OUTPUT_FILE -Encoding utf8

$codeBlock = '```'
$codeBlock | Add-Content -Path $OUTPUT_FILE -Encoding utf8

# Obtener estructura
$items = Get-ChildItem -Recurse | Where-Object { 
    $_.FullName -notlike '*.git*' -and 
    $_.FullName -notlike '*.venv*' -and 
    $_.FullName -notlike '*__pycache__*' -and 
    $_.FullName -notlike '*.pytest_cache*' -and 
    $_.Name -ne 'CONTEXT.md' 
}

foreach ($item in $items) {
    $relativePath = $item.FullName.Replace($PWD, "").TrimStart('\')
    $relativePath | Add-Content -Path $OUTPUT_FILE -Encoding utf8
}

$codeBlock | Add-Content -Path $OUTPUT_FILE -Encoding utf8
"" | Add-Content -Path $OUTPUT_FILE -Encoding utf8
"---" | Add-Content -Path $OUTPUT_FILE -Encoding utf8

# Archivos clave del sistema
Write-Host "Procesando archivos principales..." -ForegroundColor Yellow
"" | Add-Content -Path $OUTPUT_FILE -Encoding utf8
"## Contenido de Archivos Clave" | Add-Content -Path $OUTPUT_FILE -Encoding utf8
"" | Add-Content -Path $OUTPUT_FILE -Encoding utf8

$files = @("main.py", "services.py", "models.py", "schemas.py", "database.py", "requirements.txt", "Context\GOVERNANCE.md", "Context\LOGIC.md", "AGENTS.md")

foreach ($file in $files) {
    if (Test-Path $file) {
        Write-Host "  Procesando: $file" -ForegroundColor Cyan
        $ext = [System.IO.Path]::GetExtension($file).ToLower()
        $lang = if ($ext -eq ".py") { "python" } elseif ($ext -eq ".md") { "markdown" } else { "text" }
        
        "" | Add-Content -Path $OUTPUT_FILE -Encoding utf8
        "### $file" | Add-Content -Path $OUTPUT_FILE -Encoding utf8
        "" | Add-Content -Path $OUTPUT_FILE -Encoding utf8
        
        $startCode = '```' + $lang
        $startCode | Add-Content -Path $OUTPUT_FILE -Encoding utf8
        
        # Leer el contenido del archivo
        Get-Content -Path $file -Encoding utf8 | Add-Content -Path $OUTPUT_FILE -Encoding utf8
        
        $endCode = '```'
        $endCode | Add-Content -Path $OUTPUT_FILE -Encoding utf8
        
        "" | Add-Content -Path $OUTPUT_FILE -Encoding utf8
        "---" | Add-Content -Path $OUTPUT_FILE -Encoding utf8
        "" | Add-Content -Path $OUTPUT_FILE -Encoding utf8
    }
}

# Archivos de prueba importantes
Write-Host "Procesando archivos de prueba..." -ForegroundColor Yellow
"" | Add-Content -Path $OUTPUT_FILE -Encoding utf8
"## Archivos de Prueba Principales" | Add-Content -Path $OUTPUT_FILE -Encoding utf8
"" | Add-Content -Path $OUTPUT_FILE -Encoding utf8

$testFiles = @("tests\test_services.py", "tests\test_e2e_flow.py", "tests\README.md")

foreach ($file in $testFiles) {
    if (Test-Path $file) {
        Write-Host "  Procesando: $file" -ForegroundColor Cyan
        $ext = [System.IO.Path]::GetExtension($file).ToLower()
        $lang = if ($ext -eq ".py") { "python" } elseif ($ext -eq ".md") { "markdown" } else { "text" }

        "" | Add-Content -Path $OUTPUT_FILE -Encoding utf8
        "### $file" | Add-Content -Path $OUTPUT_FILE -Encoding utf8
        "" | Add-Content -Path $OUTPUT_FILE -Encoding utf8
        
        $startCode = '```' + $lang
        $startCode | Add-Content -Path $OUTPUT_FILE -Encoding utf8
        
        Get-Content -Path $file -Encoding utf8 | Add-Content -Path $OUTPUT_FILE -Encoding utf8
        
        $endCode = '```'
        $endCode | Add-Content -Path $OUTPUT_FILE -Encoding utf8
        
        "" | Add-Content -Path $OUTPUT_FILE -Encoding utf8
        "---" | Add-Content -Path $OUTPUT_FILE -Encoding utf8
        "" | Add-Content -Path $OUTPUT_FILE -Encoding utf8
    }
}

# Informacion final
"" | Add-Content -Path $OUTPUT_FILE -Encoding utf8
"## Resumen de Generacion" | Add-Content -Path $OUTPUT_FILE -Encoding utf8
"" | Add-Content -Path $OUTPUT_FILE -Encoding utf8
"- **Fecha:** $(Get-Date)" | Add-Content -Path $OUTPUT_FILE -Encoding utf8
"- **Directorio:** $PWD" | Add-Content -Path $OUTPUT_FILE -Encoding utf8

$pythonCount = (Get-ChildItem -Recurse -Filter '*.py' | Measure-Object).Count
"- **Archivos Python:** $pythonCount" | Add-Content -Path $OUTPUT_FILE -Encoding utf8

if (Test-Path 'tests') {
    $testCount = (Get-ChildItem -Path 'tests' -Filter '*.py' | Measure-Object).Count
    "- **Archivos de prueba:** $testCount" | Add-Content -Path $OUTPUT_FILE -Encoding utf8
}

$fileSize = [math]::Round((Get-Item $OUTPUT_FILE).Length / 1KB, 2)
"- **Tamaño del contexto:** $fileSize KB" | Add-Content -Path $OUTPUT_FILE -Encoding utf8
"" | Add-Content -Path $OUTPUT_FILE -Encoding utf8
"*Generado por generate_context.ps1*" | Add-Content -Path $OUTPUT_FILE -Encoding utf8

Write-Host "" 
Write-Host "Archivo $OUTPUT_FILE generado exitosamente con codificacion UTF-8!" -ForegroundColor Green
Write-Host "Tamaño: $fileSize KB" -ForegroundColor Cyan
Write-Host "Ubicacion: $PWD\$OUTPUT_FILE" -ForegroundColor Cyan
