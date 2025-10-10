# Script de Instalación Automática - CSF_DO en Docker desde Windows
# Ejecutar en PowerShell

param(
    [string]$NombreContenedor = "",
    [string]$NombreSitio = "site1.local"
)

Write-Host "`n================================================" -ForegroundColor Cyan
Write-Host "  Instalación CSF_DO (ECFDR) en Docker" -ForegroundColor Cyan
Write-Host "================================================`n" -ForegroundColor Cyan

# Función para mostrar mensajes con colores
function Write-Step {
    param([string]$Message)
    Write-Host "`n▶ $Message" -ForegroundColor Yellow
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ️  $Message" -ForegroundColor Blue
}

# Paso 1: Detectar contenedor si no se especificó
if ([string]::IsNullOrEmpty($NombreContenedor)) {
    Write-Step "Buscando contenedores de Frappe en ejecución..."
    
    $contenedores = docker ps --format "{{.Names}}" | Select-String -Pattern "frappe|erpnext|bench"
    
    if ($contenedores.Count -eq 0) {
        Write-Error-Custom "No se encontraron contenedores de Frappe en ejecución"
        Write-Info "Ejecuta 'docker ps' para ver los contenedores disponibles"
        exit 1
    }
    
    if ($contenedores.Count -eq 1) {
        $NombreContenedor = $contenedores[0].ToString()
        Write-Success "Contenedor encontrado: $NombreContenedor"
    } else {
        Write-Host "`nContenedores encontrados:" -ForegroundColor Yellow
        $i = 1
        $contenedores | ForEach-Object {
            Write-Host "  $i. $_" -ForegroundColor White
            $i++
        }
        
        $seleccion = Read-Host "`nSelecciona el número del contenedor (1-$($contenedores.Count))"
        $NombreContenedor = $contenedores[$seleccion - 1].ToString()
        Write-Success "Seleccionado: $NombreContenedor"
    }
} else {
    Write-Info "Usando contenedor: $NombreContenedor"
}

# Verificar que el contenedor existe
Write-Step "Verificando que el contenedor existe..."
$existe = docker ps --format "{{.Names}}" | Select-String -Pattern "^$NombreContenedor$"
if (-not $existe) {
    Write-Error-Custom "El contenedor '$NombreContenedor' no existe o no está en ejecución"
    Write-Info "Contenedores disponibles:"
    docker ps --format "table {{.Names}}\t{{.Status}}"
    exit 1
}
Write-Success "Contenedor verificado"

# Paso 2: Verificar sitio
Write-Step "Verificando sitio '$NombreSitio'..."
$sitios = docker exec $NombreContenedor bash -c "ls ~/frappe-bench/sites/ 2>/dev/null"
if ($sitios -match $NombreSitio) {
    Write-Success "Sitio encontrado: $NombreSitio"
} else {
    Write-Error-Custom "El sitio '$NombreSitio' no existe"
    Write-Info "Sitios disponibles:"
    docker exec $NombreContenedor bash -c "ls ~/frappe-bench/sites/"
    Write-Host "`nSi tu sitio tiene otro nombre, ejecuta:" -ForegroundColor Yellow
    Write-Host "  .\install_docker_windows.ps1 -NombreContenedor '$NombreContenedor' -NombreSitio 'TU_SITIO'" -ForegroundColor White
    exit 1
}

# Paso 3: Crear archivo de instalación en el contenedor
Write-Step "Creando script de instalación en el contenedor..."

$scriptBash = @'
#!/bin/bash
set -e

SITIO="NOMBRE_SITIO_PLACEHOLDER"
REPO_URL="https://github.com/Jovenjr/ecfdr.git"
BRANCH="ecfdr"
APP_NAME="csf_do"

echo "📦 Descargando aplicación..."
cd ~/frappe-bench
if [ -d "apps/$APP_NAME" ]; then
    echo "⚠️  Actualizando app existente..."
    cd apps/$APP_NAME
    git fetch origin
    git checkout $BRANCH
    git pull origin $BRANCH
    cd ../..
else
    bench get-app $REPO_URL --branch $BRANCH
fi

echo "📚 Instalando dependencias..."
cd apps/$APP_NAME
pip install -r requirements.txt --quiet
cd ~/frappe-bench

echo "🔍 Instalando en sitio..."
if bench --site $SITIO list-apps | grep -q $APP_NAME; then
    echo "⚠️  App ya instalada, migrando..."
else
    bench --site $SITIO install-app $APP_NAME
fi

echo "🔄 Migrando..."
bench --site $SITIO migrate

echo "🧹 Limpiando cache..."
bench --site $SITIO clear-cache
bench --site $SITIO clear-website-cache

echo "🔄 Reiniciando..."
bench restart

echo "✅ Instalación completada!"
bench --site $SITIO list-apps
'@

$scriptBash = $scriptBash.Replace("NOMBRE_SITIO_PLACEHOLDER", $NombreSitio)

# Guardar script temporalmente
$scriptBash | Out-File -FilePath "temp_install.sh" -Encoding ASCII -NoNewline

# Copiar al contenedor
docker cp temp_install.sh ${NombreContenedor}:/tmp/install_csf_do.sh
Remove-Item temp_install.sh

Write-Success "Script creado en el contenedor"

# Paso 4: Ejecutar instalación
Write-Step "Ejecutando instalación en el contenedor..."
Write-Info "Este proceso puede tardar varios minutos..."
Write-Host ""

try {
    docker exec -it $NombreContenedor bash -c "chmod +x /tmp/install_csf_do.sh && /tmp/install_csf_do.sh"
    Write-Success "Instalación completada exitosamente"
} catch {
    Write-Error-Custom "Error durante la instalación"
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}

# Paso 5: Verificación
Write-Step "Verificando instalación..."
$apps = docker exec $NombreContenedor bash -c "bench --site $NombreSitio list-apps"

if ($apps -match "csf_do") {
    Write-Success "CSF_DO está instalado correctamente"
} else {
    Write-Error-Custom "No se pudo verificar la instalación"
}

# Instrucciones finales
Write-Host "`n================================================" -ForegroundColor Cyan
Write-Host "  🎉 Instalación Completada" -ForegroundColor Cyan
Write-Host "================================================`n" -ForegroundColor Cyan

Write-Host "📋 Apps instaladas en $NombreSitio`:" -ForegroundColor Yellow
Write-Host $apps

Write-Host "`n📖 Próximos pasos:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Configurar el simulador:" -ForegroundColor White
Write-Host "   - Abrir ERPNext en tu navegador" -ForegroundColor Gray
Write-Host "   - Buscar: 'DGII Configuration'" -ForegroundColor Gray
Write-Host "   - Establecer 'Modo API' = simulator" -ForegroundColor Gray
Write-Host "   - Completar RNC Emisor" -ForegroundColor Gray
Write-Host "   - Guardar" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Probar el simulador:" -ForegroundColor White
Write-Host "   docker exec -it $NombreContenedor bash" -ForegroundColor Gray
Write-Host "   bench --site $NombreSitio console" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Leer documentación:" -ForegroundColor White
Write-Host "   - INICIO_RAPIDO.md" -ForegroundColor Gray
Write-Host "   - GUIA_RAPIDA_SIMULADOR.md" -ForegroundColor Gray
Write-Host "   - INSTRUCCIONES_PRUEBA.md" -ForegroundColor Gray
Write-Host ""

Write-Host "================================================`n" -ForegroundColor Cyan
Write-Host "✅ ¡Listo para usar!" -ForegroundColor Green
Write-Host ""

# Limpiar
docker exec $NombreContenedor bash -c "rm -f /tmp/install_csf_do.sh"
