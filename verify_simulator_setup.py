#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Verificación de Instalación del Simulador DGII
=========================================================

Este script verifica que todo esté correctamente instalado y configurado
para usar el simulador DGII.

Uso:
    python verify_simulator_setup.py
"""

import sys
import os

# Agregar el directorio de la aplicación al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'csf_do'))

def print_header(title):
    """Imprime un encabezado formateado"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def check_item(name, condition, message_ok, message_error):
    """Verifica un item y muestra el resultado"""
    if condition:
        print(f"  ✅ {name}")
        if message_ok:
            print(f"     {message_ok}")
        return True
    else:
        print(f"  ❌ {name}")
        print(f"     {message_error}")
        return False

def main():
    """Función principal"""
    print("\n🔍 VERIFICACIÓN DE INSTALACIÓN - SIMULADOR DGII")
    
    checks_passed = 0
    checks_total = 0
    
    # 1. Verificar estructura de archivos
    print_header("1. Verificación de Archivos")
    
    files_to_check = [
        ("Simulador principal", "csf_do/csf_do/integrations/dgii_simulator.py"),
        ("Cliente DGII", "csf_do/csf_do/integrations/dgii_client.py"),
        ("Parser ACECFAR", "csf_do/csf_do/utils/acecfar_parser.py"),
        ("Validador de firma", "csf_do/csf_do/utils/signature_validator.py"),
        ("Procesador ACECFAR", "csf_do/csf_do/integrations/acecfar_processor.py"),
        ("Tests simulador", "csf_do/csf_do/tests/test_dgii_simulator.py"),
        ("Tests ACECFAR", "csf_do/csf_do/tests/test_acecfar.py"),
        ("Script de pruebas", "test_simulator_complete.py"),
        ("Guía rápida", "GUIA_RAPIDA_SIMULADOR.md"),
    ]
    
    for name, filepath in files_to_check:
        checks_total += 1
        exists = os.path.exists(filepath)
        if check_item(
            name,
            exists,
            f"Archivo encontrado: {filepath}",
            f"Archivo no encontrado: {filepath}"
        ):
            checks_passed += 1
    
    # 2. Verificar importaciones
    print_header("2. Verificación de Importaciones")
    
    imports_to_check = [
        ("Frappe Framework", "frappe"),
        ("Requests", "requests"),
        ("Cryptography", "cryptography"),
        ("lxml", "lxml"),
    ]
    
    for name, module_name in imports_to_check:
        checks_total += 1
        try:
            __import__(module_name)
            if check_item(
                name,
                True,
                f"Módulo {module_name} disponible",
                ""
            ):
                checks_passed += 1
        except ImportError:
            check_item(
                name,
                False,
                "",
                f"Módulo {module_name} no instalado. Instalar con: pip install {module_name}"
            )
    
    # 3. Verificar módulos del proyecto
    print_header("3. Verificación de Módulos del Proyecto")
    
    project_modules = [
        ("Simulador DGII", "csf_do.csf_do.integrations.dgii_simulator"),
        ("Cliente DGII", "csf_do.csf_do.integrations.dgii_client"),
        ("Parser ACECFAR", "csf_do.csf_do.utils.acecfar_parser"),
        ("Validador firma", "csf_do.csf_do.utils.signature_validator"),
    ]
    
    for name, module_name in project_modules:
        checks_total += 1
        try:
            __import__(module_name)
            if check_item(
                name,
                True,
                f"Módulo {module_name} importado correctamente",
                ""
            ):
                checks_passed += 1
        except ImportError as e:
            check_item(
                name,
                False,
                "",
                f"Error al importar {module_name}: {str(e)}"
            )
    
    # 4. Verificar DocTypes (solo si Frappe está disponible)
    print_header("4. Verificación de DocTypes (requiere Frappe)")
    
    try:
        import frappe
        frappe_available = True
    except ImportError:
        frappe_available = False
        print("  ⚠️  Frappe no está disponible")
        print("     Ejecute dentro del contexto de Frappe/ERPNext para verificación completa")
    
    if frappe_available:
        doctypes_to_check = [
            "DGII Configuration",
            "DGII Simulator Config",
            "e-CF Recibido",
        ]
        
        for doctype in doctypes_to_check:
            checks_total += 1
            # Nota: Esta verificación solo funciona dentro de frappe bench
            print(f"  ℹ️  {doctype}")
            print(f"     Verificar manualmente en ERPNext")
    
    # 5. Verificar documentación
    print_header("5. Verificación de Documentación")
    
    docs_to_check = [
        ("Guía rápida", "GUIA_RAPIDA_SIMULADOR.md"),
        ("Resumen simulador", "RESUMEN_SIMULADOR.md"),
        ("Progreso implementación", "PROGRESO_IMPLEMENTACION.md"),
        ("Plan implementación", "PLAN_IMPLEMENTACION.md"),
    ]
    
    for name, filepath in docs_to_check:
        checks_total += 1
        exists = os.path.exists(filepath)
        if check_item(
            name,
            exists,
            f"Documento encontrado: {filepath}",
            f"Documento no encontrado: {filepath}"
        ):
            checks_passed += 1
    
    # Resumen final
    print_header("RESUMEN DE VERIFICACIÓN")
    
    percentage = (checks_passed / checks_total * 100) if checks_total > 0 else 0
    
    print(f"\n  Total de verificaciones: {checks_total}")
    print(f"  ✅ Exitosas: {checks_passed}")
    print(f"  ❌ Fallidas: {checks_total - checks_passed}")
    print(f"  📊 Porcentaje: {percentage:.1f}%")
    
    if checks_passed == checks_total:
        print("\n  🎉 ¡TODO VERIFICADO CORRECTAMENTE!")
        print("     El simulador está listo para usar.")
        print("\n  📖 Siguiente paso: Leer GUIA_RAPIDA_SIMULADOR.md")
    elif checks_passed >= checks_total * 0.8:
        print("\n  ⚠️  LA MAYORÍA DE VERIFICACIONES PASARON")
        print("     Revisar elementos fallidos antes de continuar.")
    else:
        print("\n  ❌ MÚLTIPLES VERIFICACIONES FALLARON")
        print("     Revisar la instalación antes de continuar.")
    
    print("\n" + "="*70)
    
    # Instrucciones adicionales
    print("\n📋 INSTRUCCIONES:")
    print("\n  Para verificación completa dentro de Frappe/ERPNext:")
    print("    1. cd [frappe-bench]")
    print("    2. bench --site [tu-sitio] console")
    print("    3. Ejecutar: exec(open('path/to/verify_simulator_setup.py').read())")
    print("\n  Para ejecutar pruebas:")
    print("    python test_simulator_complete.py")
    print("\n  Para iniciar desarrollo:")
    print("    Leer GUIA_RAPIDA_SIMULADOR.md")
    print()
    
    return 0 if checks_passed == checks_total else 1

if __name__ == "__main__":
    sys.exit(main())
