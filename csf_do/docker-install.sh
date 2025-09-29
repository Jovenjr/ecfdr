#!/bin/bash
# Script de instalación para Docker ERPNext
# Copyright (c) 2025, Navari Ltd and contributors

echo "🐳 Instalando CSF DO en ERPNext Docker..."

# Verificar que estamos en el contenedor correcto
if [ ! -f "/home/frappe/frappe-bench/current/frappe/frappe/__init__.py" ]; then
    echo "❌ Error: No se detectó entorno Frappe/ERPNext"
    exit 1
fi

# Navegar al directorio del bench
cd /home/frappe/frappe-bench

# Crear directorio para la aplicación
echo "📁 Creando directorio para CSF DO..."
mkdir -p apps/csf_do

# Copiar archivos de la aplicación
echo "📋 Copiando archivos de la aplicación..."
cp -r /tmp/csf_do/* apps/csf_do/

# Instalar la aplicación
echo "⚙️ Instalando CSF DO..."
bench get-app --branch main file:///tmp/csf_do

# Instalar en el sitio
echo "🔧 Instalando en el sitio..."
bench --site all install-app csf_do

# Ejecutar migraciones
echo "🔄 Ejecutando migraciones..."
bench --site all migrate

# Reiniciar servicios
echo "🔄 Reiniciando servicios..."
bench restart

echo "✅ CSF DO instalado exitosamente en ERPNext Docker!"
echo "🌐 Accede a tu ERPNext en: http://localhost:8000"
echo "📋 Módulo CSF DO disponible en el menú principal"
