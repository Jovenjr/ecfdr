# Script de instalacion para Docker ERPNext - PowerShell
# Copyright (c) 2025, Navari Ltd and contributors

Write-Host "INSTALACION DE CSF DO EN DOCKER ERPNext" -ForegroundColor Green
Write-Host "=======================================" -ForegroundColor Green

# Verificar que Docker este corriendo
try {
    $dockerPs = docker ps 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "Docker no esta corriendo"
    }
} catch {
    Write-Host "Error: Docker no esta corriendo" -ForegroundColor Red
    exit 1
}

# Verificar que ERPNext este corriendo
$erpnextContainer = docker ps --format "table {{.Names}}" | Select-String -Pattern "(backend|frappe)" | Select-Object -First 1

if (-not $erpnextContainer) {
    Write-Host "Error: ERPNext no esta corriendo en Docker" -ForegroundColor Red
    exit 1
}

$containerName = $erpnextContainer.Line.Trim()
Write-Host "Docker y ERPNext detectados correctamente" -ForegroundColor Green
Write-Host "Contenedor backend encontrado: $containerName" -ForegroundColor Yellow

# Crear directorio temporal para la aplicacion
Write-Host "Preparando archivos de la aplicacion..." -ForegroundColor Yellow
$tempDir = "temp_csf_do"
if (Test-Path $tempDir) {
    Remove-Item -Recurse -Force $tempDir
}
New-Item -ItemType Directory -Path $tempDir | Out-Null
Copy-Item -Recurse -Path "csf_do\*" -Destination $tempDir

# Copiar archivos al contenedor
Write-Host "Copiando archivos al contenedor..." -ForegroundColor Yellow
docker cp $tempDir $containerName`:/tmp/csf_do

# Ejecutar instalacion en el contenedor
Write-Host "Ejecutando instalacion en el contenedor..." -ForegroundColor Yellow

# Paso 1: Obtener la aplicacion
Write-Host "Paso 1: Obteniendo la aplicacion..." -ForegroundColor Cyan
docker exec -it $containerName bash -c "cd /home/frappe/frappe-bench && bench get-app --branch main file:///tmp/csf_do"

# Paso 2: Instalar en el sitio
Write-Host "Paso 2: Instalando en el sitio..." -ForegroundColor Cyan
docker exec -it $containerName bash -c "cd /home/frappe/frappe-bench && bench --site all install-app csf_do"

# Paso 3: Ejecutar migraciones
Write-Host "Paso 3: Ejecutando migraciones..." -ForegroundColor Cyan
docker exec -it $containerName bash -c "cd /home/frappe/frappe-bench && bench --site all migrate"

# Paso 4: Reiniciar servicios
Write-Host "Paso 4: Reiniciando servicios..." -ForegroundColor Cyan
docker exec -it $containerName bash -c "cd /home/frappe/frappe-bench && bench restart"

# Limpiar archivos temporales
Write-Host "Limpiando archivos temporales..." -ForegroundColor Yellow
Remove-Item -Recurse -Force $tempDir

Write-Host ""
Write-Host "INSTALACION COMPLETADA EXITOSAMENTE!" -ForegroundColor Green
Write-Host "Accede a tu ERPNext en: http://localhost:8000" -ForegroundColor Cyan
Write-Host "El modulo CSF DO estara disponible en el menu principal" -ForegroundColor Cyan
Write-Host ""
Write-Host "Para verificar la instalacion:" -ForegroundColor Yellow
Write-Host "docker exec -it $containerName bench --site all list-apps" -ForegroundColor White
