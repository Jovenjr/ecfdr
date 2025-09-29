#!/usr/bin/env python3
# Copyright (c) 2025, Navari Ltd and contributors
# For license information, please see license.txt

"""
Script de prueba para verificar la instalación de CSF DO
Este script verifica que todos los archivos estén en su lugar
"""

import os
import sys

def test_file_structure():
    """Verificar que la estructura de archivos esté correcta"""
    base_path = os.path.dirname(os.path.abspath(__file__))
    
    required_files = [
        "install/install.py",
        "install/validate_installation.py", 
        "install/setup_initial_data.py",
        "install/__init__.py",
        "config/permissions.py",
        "config/site_config.py",
        "config/reports.py",
        "config/environment.py",
        "config/backup.py",
        "config/system_config.py",
        "utils/validate_integrity.py",
        "utils/data_validation.py",
        "tests/test_installation.py",
        "scripts/setup_initial_config.py",
        "patches/v2_1_6_setup_initial_data.py",
        "docs/INSTALACION.md",
        "docs/COMPLETADO.md",
        "hooks.py",
        "modules.txt",
        "patches.txt",
    ]
    
    missing_files = []
    existing_files = []
    
    for file_path in required_files:
        full_path = os.path.join(base_path, file_path)
        if os.path.exists(full_path):
            existing_files.append(file_path)
        else:
            missing_files.append(file_path)
    
    print("=== VERIFICACIÓN DE ESTRUCTURA DE ARCHIVOS ===")
    print(f"[OK] Archivos encontrados: {len(existing_files)}")
    print(f"[ERROR] Archivos faltantes: {len(missing_files)}")
    
    if existing_files:
        print("\nArchivos existentes:")
        for file in existing_files:
            print(f"  [OK] {file}")
    
    if missing_files:
        print("\nArchivos faltantes:")
        for file in missing_files:
            print(f"  [ERROR] {file}")

    assert len(missing_files) == 0, f"Faltan {len(missing_files)} archivos requeridos"

def test_python_imports():
    """Verificar que los módulos Python se pueden importar"""
    print("\n=== VERIFICACIÓN DE IMPORTACIONES PYTHON ===")
    
    try:
        import csf_do
        print("[OK] csf_do importado correctamente")
    except ImportError as e:
        print(f"[ERROR] Error importando csf_do: {e}")
        assert False, f"Error importando csf_do: {e}"
    
    # Verificar módulos que no dependen de Frappe
    try:
        from csf_do.config.system_config import get_system_config
        print("[OK] Modulos de configuracion importados correctamente")
    except ImportError as e:
        print(f"[ERROR] Error importando modulos de configuracion: {e}")
        assert False, f"Error importando modulos de configuracion: {e}"

    assert True

def test_requirements():
    """Verificar que las dependencias estén instaladas"""
    print("\n=== VERIFICACIÓN DE DEPENDENCIAS ===")
    
    required_packages = [
        "qrcode",
        "lxml", 
        "signxml",
        "cryptography",
        "requests"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"[OK] {package} instalado")
        except ImportError:
            print(f"[ERROR] {package} NO instalado")
            missing_packages.append(package)

    assert len(missing_packages) == 0, f"Faltan instalar los siguientes paquetes: {missing_packages}"

def main():
    """Función principal de prueba"""
    print("INICIANDO PRUEBAS DE INSTALACION CSF DO")
    print("=" * 50)
    
    # Ejecutar pruebas
    structure_ok = test_file_structure()
    imports_ok = test_python_imports()
    requirements_ok = test_requirements()
    
    print("\n" + "=" * 50)
    print("RESUMEN DE PRUEBAS")
    print("=" * 50)
    
    if structure_ok:
        print("[OK] Estructura de archivos: CORRECTA")
    else:
        print("[ERROR] Estructura de archivos: FALTAN ARCHIVOS")
    
    if imports_ok:
        print("[OK] Importaciones Python: CORRECTAS")
    else:
        print("[ERROR] Importaciones Python: ERRORES")
    
    if requirements_ok:
        print("[OK] Dependencias: INSTALADAS")
    else:
        print("[ERROR] Dependencias: FALTANTES")
    
    if structure_ok and imports_ok and requirements_ok:
        print("\n[SUCCESS] INSTALACION COMPLETADA EXITOSAMENTE!")
        print("La aplicacion CSF DO esta lista para ser instalada en ERPNext")
        return True
    else:
        print("\n[WARNING] INSTALACION INCOMPLETA")
        print("Revisar los errores anteriores antes de proceder")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
