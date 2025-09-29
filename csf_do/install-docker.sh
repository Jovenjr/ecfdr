#!/bin/bash
# Script de instalación manual para Docker ERPNext
# Copyright (c) 2025, Navari Ltd and contributors

echo "🐳 INSTALACIÓN MANUAL DE CSF DO EN DOCKER ERPNext"
echo "=================================================="

# Verificar que Docker esté corriendo
if ! docker ps > /dev/null 2>&1; then
    echo "❌ Error: Docker no está corriendo"
    exit 1
fi

# Verificar que ERPNext esté corriendo
if ! docker ps | grep -q "frappe/erpnext"; then
    echo "❌ Error: ERPNext no está corriendo en Docker"
    exit 1
fi

echo "✅ Docker y ERPNext detectados correctamente"

# Obtener el nombre del contenedor backend
BACKEND_CONTAINER=$(docker ps --format "table {{.Names}}" | grep -E "(backend|frappe)" | head -1)

if [ -z "$BACKEND_CONTAINER" ]; then
    echo "❌ Error: No se pudo encontrar el contenedor backend de ERPNext"
    exit 1
fi

echo "📦 Contenedor backend encontrado: $BACKEND_CONTAINER"

# Crear directorio temporal para la aplicación
echo "📁 Preparando archivos de la aplicación..."
mkdir -p temp_csf_do
cp -r csf_do/* temp_csf_do/

# Copiar archivos al contenedor
echo "📋 Copiando archivos al contenedor..."
docker cp temp_csf_do $BACKEND_CONTAINER:/tmp/csf_do

# Ejecutar instalación en el contenedor
echo "⚙️ Ejecutando instalación en el contenedor..."
docker exec -it $BACKEND_CONTAINER bash -c "
    cd /home/frappe/frappe-bench && \
    bench get-app --branch main file:///tmp/csf_do && \
    bench --site all install-app csf_do && \
    bench --site all migrate && \
    bench restart
"

# Limpiar archivos temporales
echo "🧹 Limpiando archivos temporales..."
rm -rf temp_csf_do

echo ""
echo "✅ INSTALACIÓN COMPLETADA EXITOSAMENTE!"
echo "🌐 Accede a tu ERPNext en: http://localhost:8000"
echo "📋 El módulo CSF DO estará disponible en el menú principal"
echo ""
echo "🔧 Para verificar la instalación:"
echo "   docker exec -it $BACKEND_CONTAINER bench --site all list-apps"
