#!/bin/bash
# Script de Instalación Rápida - CSF_DO en Docker
# Ejecutar este script DENTRO del contenedor Docker de Frappe

set -e  # Salir si hay algún error

echo "================================================"
echo "  Instalación CSF_DO (ECFDR) desde GitHub"
echo "================================================"
echo ""

# Variables (MODIFICA SEGÚN TU CONFIGURACIÓN)
SITIO="site1.local"  # Cambiar por el nombre de tu sitio
REPO_URL="https://github.com/Jovenjr/ecfdr.git"
BRANCH="ecfdr"
APP_NAME="csf_do"

echo "📋 Configuración:"
echo "   Sitio: $SITIO"
echo "   Repositorio: $REPO_URL"
echo "   Rama: $BRANCH"
echo "   App: $APP_NAME"
echo ""

# Verificar que estamos en el directorio correcto
if [ ! -d "apps" ]; then
    echo "❌ Error: No estamos en el directorio bench"
    echo "   Ejecuta: cd ~/frappe-bench"
    exit 1
fi

echo "✅ Directorio bench encontrado"
echo ""

# Paso 1: Descargar la app
echo "📦 Paso 1/6: Descargando aplicación desde GitHub..."
if [ -d "apps/$APP_NAME" ]; then
    echo "⚠️  La app ya existe. Actualizando..."
    cd apps/$APP_NAME
    git fetch origin
    git checkout $BRANCH
    git pull origin $BRANCH
    cd ../..
else
    bench get-app $REPO_URL --branch $BRANCH
fi
echo "✅ Aplicación descargada"
echo ""

# Paso 2: Instalar dependencias
echo "📚 Paso 2/6: Instalando dependencias Python..."
cd apps/$APP_NAME
pip install -r requirements.txt --quiet
cd ../..
echo "✅ Dependencias instaladas"
echo ""

# Paso 3: Verificar si la app ya está instalada en el sitio
echo "🔍 Paso 3/6: Verificando instalación en el sitio..."
if bench --site $SITIO list-apps | grep -q $APP_NAME; then
    echo "⚠️  La app ya está instalada en el sitio"
    ALREADY_INSTALLED=true
else
    echo "📥 Instalando app en el sitio..."
    bench --site $SITIO install-app $APP_NAME
    ALREADY_INSTALLED=false
fi
echo "✅ App en el sitio"
echo ""

# Paso 4: Migrar
echo "🔄 Paso 4/6: Ejecutando migraciones..."
bench --site $SITIO migrate
echo "✅ Migraciones completadas"
echo ""

# Paso 5: Limpiar cache
echo "🧹 Paso 5/6: Limpiando cache..."
bench --site $SITIO clear-cache
bench --site $SITIO clear-website-cache
echo "✅ Cache limpiado"
echo ""

# Paso 6: Reiniciar
echo "🔄 Paso 6/6: Reiniciando bench..."
bench restart
echo "✅ Bench reiniciado"
echo ""

# Verificación final
echo "================================================"
echo "  🎉 Instalación Completada"
echo "================================================"
echo ""
echo "📋 Apps instaladas:"
bench --site $SITIO list-apps
echo ""

# Instrucciones finales
echo "📖 Próximos pasos:"
echo ""
echo "1. Configurar el simulador en ERPNext:"
echo "   - Ir a: DGII Configuration"
echo "   - Establecer 'Modo API' = simulator"
echo "   - Completar RNC Emisor y URLs"
echo "   - Guardar"
echo ""
echo "2. Probar el simulador:"
echo "   bench --site $SITIO console"
echo "   >>> from csf_do.csf_do.integrations.dgii_client import get_dgii_client"
echo "   >>> client = get_dgii_client()"
echo "   >>> print(client.get_info())"
echo ""
echo "3. Leer la documentación:"
echo "   - INICIO_RAPIDO.md"
echo "   - GUIA_RAPIDA_SIMULADOR.md"
echo "   - INSTRUCCIONES_PRUEBA.md"
echo ""
echo "================================================"
echo ""

if [ "$ALREADY_INSTALLED" = false ]; then
    echo "✅ ¡La aplicación se instaló correctamente!"
else
    echo "✅ ¡La aplicación se actualizó correctamente!"
fi

echo ""
echo "🚀 ¡Listo para usar!"
echo ""
