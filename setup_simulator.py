#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Instalación Rápida - Simulador DGII
==============================================

Este script configura automáticamente el simulador DGII si es necesario.

Uso:
    python setup_simulator.py
"""

import sys
import os
import json

def print_header(title):
    """Imprime un encabezado formateado"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def print_step(step, description):
    """Imprime un paso"""
    print(f"\n{step}. {description}")

def main():
    """Función principal"""
    print("\n🔧 CONFIGURACIÓN AUTOMÁTICA - SIMULADOR DGII")
    
    print_header("INFORMACIÓN")
    print("\n  Este script verifica y configura el simulador DGII.")
    print("  No requiere conexión a DGII - es completamente local.")
    
    # 1. Verificar dependencias
    print_step("1", "Verificando dependencias...")
    
    dependencies = {
        "frappe": "Frappe Framework",
        "requests": "Biblioteca HTTP",
        "lxml": "Parser XML",
        "cryptography": "Validación de firmas"
    }
    
    missing = []
    for module, name in dependencies.items():
        try:
            __import__(module)
            print(f"   ✅ {name}")
        except ImportError:
            print(f"   ❌ {name} - NO INSTALADO")
            missing.append(module)
    
    if missing:
        print("\n   ⚠️  Dependencias faltantes detectadas.")
        print("\n   Instalar con:")
        print(f"   pip install {' '.join(missing)}")
        return 1
    
    # 2. Verificar estructura
    print_step("2", "Verificando estructura de archivos...")
    
    required_files = [
        "csf_do/csf_do/integrations/dgii_simulator.py",
        "csf_do/csf_do/integrations/dgii_client.py",
        "csf_do/csf_do/doctype/dgii_configuration/dgii_configuration.json",
    ]
    
    all_present = True
    for filepath in required_files:
        if os.path.exists(filepath):
            print(f"   ✅ {filepath}")
        else:
            print(f"   ❌ {filepath} - NO ENCONTRADO")
            all_present = False
    
    if not all_present:
        print("\n   ❌ Algunos archivos están faltando.")
        print("   Verificar que el proyecto esté completo.")
        return 1
    
    # 3. Instrucciones de configuración
    print_step("3", "Configuración en ERPNext")
    
    print("\n   Para activar el simulador:")
    print("   1. Abrir ERPNext")
    print("   2. Ir a: DGII Configuration")
    print("   3. Establecer 'Modo API' = simulator")
    print("   4. Completar campos obligatorios:")
    print("      - RNC Emisor: Tu RNC")
    print("      - Versión e-CF: 1.0")
    print("      - Pre-Certificación Base URL: https://ecf.dgii.gov.do/testecf/")
    print("      - Certificación Base URL: https://ecf.dgii.gov.do/certecf/")
    print("      - Producción Base URL: https://ecf.dgii.gov.do/ecf/")
    print("   5. Guardar")
    
    # 4. Próximos pasos
    print_step("4", "Próximos pasos")
    
    print("\n   ✅ Ejecutar pruebas:")
    print("      python test_simulator_complete.py")
    print("\n   ✅ Verificar instalación:")
    print("      python verify_simulator_setup.py")
    print("\n   📖 Leer documentación:")
    print("      - INICIO_RAPIDO.md")
    print("      - GUIA_RAPIDA_SIMULADOR.md")
    print("      - TRABAJO_COMPLETADO.md")
    
    print_header("RESUMEN")
    print("\n  ✅ Dependencias instaladas")
    print("  ✅ Archivos presentes")
    print("  ⏳ Configurar en ERPNext (manual)")
    print("\n  Estado: LISTO PARA CONFIGURAR")
    print("\n" + "="*70)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
