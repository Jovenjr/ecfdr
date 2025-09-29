#!/bin/bash
# Script de instalación dentro del contenedor Docker
# Copyright (c) 2025, Navari Ltd and contributors

echo "Instalando CSF DO en el contenedor..."

# Navegar al directorio del bench
cd /home/frappe/frappe-bench

# Agregar la aplicación al PYTHONPATH
export PYTHONPATH="/home/frappe/frappe-bench/apps/csf_do:$PYTHONPATH"

# Verificar que la aplicación se puede importar
echo "Verificando importación de la aplicación..."
python -c "import sys; sys.path.insert(0, '/home/frappe/frappe-bench/apps/csf_do'); import csf_do; print('Aplicación importada correctamente')"

# Instalar la aplicación usando bench
echo "Instalando la aplicación en el sitio..."
bench --site all install-app csf_do

# Ejecutar migraciones
echo "Ejecutando migraciones..."
bench --site all migrate

# Reiniciar servicios
echo "Reiniciando servicios..."
bench restart

echo "Instalación completada!"
