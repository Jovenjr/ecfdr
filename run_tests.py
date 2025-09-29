#!/usr/bin/env python3
"""
Script maestro para ejecutar pruebas de ECFDR

Uso:
- Local: python run_tests.py
- Docker: docker exec -it erpnext-backend-1 python /home/frappe/frappe-bench/apps/csf_do/run_tests.py
"""

import os
import sys
import subprocess
import argparse

def run_local_tests():
    """Ejecutar pruebas locales (sin dependencias de Frappe)"""
    print("🏠 Ejecutando pruebas LOCALES...")
    return subprocess.run([sys.executable, 'test_ecfdr_integration.py'], cwd=os.path.dirname(__file__)).returncode == 0

def run_docker_tests():
    """Ejecutar pruebas en Docker (con Frappe)"""
    print("🐳 Ejecutando pruebas en DOCKER...")
    return subprocess.run([sys.executable, 'test_ecfdr_docker.py']).returncode == 0

def run_full_test_suite():
    """Ejecutar suite completa de pruebas"""
    print("🚀 Ejecutando SUITE COMPLETA de pruebas ECFDR")
    print("=" * 60)

    # Pruebas locales primero
    print("\n📍 FASE 1: Pruebas locales")
    local_success = run_local_tests()

    # Pruebas en Docker
    print("\n📍 FASE 2: Pruebas en Docker")
    docker_success = run_docker_tests()

    # Resultado final
    print("\n" + "=" * 60)
    print("🎯 RESULTADO FINAL")
    print("=" * 60)

    if local_success and docker_success:
        print("✅ TODAS LAS PRUEBAS PASARON")
        print("🎉 ECFDR está completamente funcional")
        return True
    else:
        print("❌ ALGUNAS PRUEBAS FALLARON")
        if not local_success:
            print("  - Fallaron pruebas locales")
        if not docker_success:
            print("  - Fallaron pruebas en Docker")
        return False

def main():
    parser = argparse.ArgumentParser(description='Ejecutar pruebas ECFDR')
    parser.add_argument('--local', action='store_true', help='Solo pruebas locales')
    parser.add_argument('--docker', action='store_true', help='Solo pruebas en Docker')
    parser.add_argument('--full', action='store_true', help='Suite completa (default)')

    args = parser.parse_args()

    # Si no se especifica nada, ejecutar suite completa
    if not any([args.local, args.docker, args.full]):
        args.full = True

    if args.local:
        success = run_local_tests()
    elif args.docker:
        success = run_docker_tests()
    else:  # args.full
        success = run_full_test_suite()

    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())
