# Script de instalación para Docker ERPNext - PowerShell
# Copyright (c) 2025, Navari Ltd and contributors

Write-Host "🐳 INSTALACIÓN DE CSF DO EN DOCKER ERPNext" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green

# Verificar que Docker esté corriendo
try {
    $dockerPs = docker ps 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "Docker no está corriendo"
    }
} catch {
    Write-Host "❌ Error: Docker no está corriendo" -ForegroundColor Red
    exit 1
}

# Verificar que ERPNext esté corriendo
$erpnextContainer = docker ps --format "table {{.Names}}" | Select-String -Pattern "(backend|frappe)" | Select-Object -First 1

if (-not $erpnextContainer) {
    Write-Host "❌ Error: ERPNext no está corriendo en Docker" -ForegroundColor Red
    exit 1
}

$containerName = $erpnextContainer.Line.Trim()
Write-Host "✅ Docker y ERPNext detectados correctamente" -ForegroundColor Green
Write-Host "📦 Contenedor backend encontrado: $containerName" -ForegroundColor Yellow

# Crear directorio temporal para la aplicación
Write-Host "📁 Preparando archivos de la aplicación..." -ForegroundColor Yellow
$tempDir = "temp_csf_do"
if (Test-Path $tempDir) {
    Remove-Item -Recurse -Force $tempDir
}
New-Item -ItemType Directory -Path $tempDir | Out-Null
Copy-Item -Recurse -Path "csf_do\*" -Destination $tempDir

# Copiar archivos al contenedor
Write-Host "📋 Copiando archivos al contenedor..." -ForegroundColor Yellow
docker cp $tempDir $containerName`:/tmp/csf_do

# Ejecutar instalación en el contenedor
Write-Host "⚙️ Ejecutando instalación en el contenedor..." -ForegroundColor Yellow
$installCommand = @"
cd /home/frappe/frappe-bench && 
bench get-app --branch main file:///tmp/csf_do && 
bench --site all install-app csf_do && 
bench --site all migrate && 
bench restart
"@

docker exec -it $containerName bash -c $installCommand

# Limpiar archivos temporales
Write-Host "🧹 Limpiando archivos temporales..." -ForegroundColor Yellow
Remove-Item -Recurse -Force $tempDir

Write-Host ""
Write-Host "✅ INSTALACIÓN COMPLETADA EXITOSAMENTE!" -ForegroundColor Green
Write-Host "🌐 Accede a tu ERPNext en: http://localhost:8000" -ForegroundColor Cyan
Write-Host "📋 El módulo CSF DO estará disponible en el menú principal" -ForegroundColor Cyan
Write-Host ""
Write-Host "🔧 Para verificar la instalación:" -ForegroundColor Yellow
Write-Host "   docker exec -it $containerName bench --site all list-apps" -ForegroundColor White
