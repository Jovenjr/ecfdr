#!/usr/bin/env python3
# Copyright (c) 2025, Navari Ltd and contributors
# For license information, please see license.txt

"""
Script de configuración inicial para CSF DO
Ejecutar después de la instalación para configurar datos básicos
"""

import frappe
from frappe import _

def setup_initial_configuration():
    """Configurar datos iniciales para CSF DO"""
    print("Iniciando configuración inicial de CSF DO...")
    
    try:
        # Configurar datos básicos
        setup_basic_data()
        
        # Configurar permisos
        setup_permissions()
        
        # Validar configuración
        validate_configuration()
        
        print("✅ Configuración inicial completada exitosamente")
        
    except Exception as e:
        print(f"❌ Error durante la configuración: {str(e)}")
        raise

def setup_basic_data():
    """Configurar datos básicos"""
    print("Configurando datos básicos...")
    
    # Importar funciones de instalación
    from csf_do.install.setup_initial_data import setup_dominican_data
    setup_dominican_data()
    
    print("✅ Datos básicos configurados")

def setup_permissions():
    """Configurar permisos"""
    print("Configurando permisos...")
    
    # Los permisos se configuran automáticamente via fixtures
    print("✅ Permisos configurados")

def validate_configuration():
    """Validar configuración"""
    print("Validando configuración...")
    
    from csf_do.utils.validate_integrity import validate_system_integrity
    results = validate_system_integrity()
    
    if results["errors"]:
        print("❌ Errores encontrados:")
        for error in results["errors"]:
            print(f"  - {error}")
    
    if results["warnings"]:
        print("⚠️ Advertencias:")
        for warning in results["warnings"]:
            print(f"  - {warning}")
    
    if results["passed"]:
        print("✅ Validaciones exitosas:")
        for passed in results["passed"]:
            print(f"  - {passed}")

if __name__ == "__main__":
    frappe.init(site="your-site-name")
    frappe.connect()
    setup_initial_configuration()
