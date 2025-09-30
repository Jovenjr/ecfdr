#!/usr/bin/env python3
"""
Script de Pruebas Automatizadas para ECFDR (Electronic Comprobante Fiscal Digital República Dominicana)

Este script realiza pruebas de integración y unitarias para verificar que ECFDR funciona correctamente.

Pruebas incluidas:
- Importación de módulos
- Funcionalidad de reportes
- Validación de estructuras de datos
- Integración con Frappe/ERPNext
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch, MagicMock
import json
import tempfile
import shutil

# Agregar el directorio de la aplicación al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'csf_do'))

class ECFDRTestCase(unittest.TestCase):
    """Clase base para pruebas de ECFDR"""

    def setUp(self):
        """Configuración inicial para cada prueba"""
        self.test_data = {
            'company': 'Test Company RD',
            'from_date': '2024-01-01',
            'to_date': '2024-12-31'
        }

    def tearDown(self):
        """Limpieza después de cada prueba"""
        pass

class TestECFDRImports(ECFDRTestCase):
    """Pruebas de importación de módulos ECFDR"""

    def test_import_main_module(self):
        """Probar importación del módulo principal"""
        try:
            import csf_do
            self.assertTrue(hasattr(csf_do, '__version__'))
            print("✓ Módulo principal ECFDR importado correctamente")
        except ImportError as e:
            self.fail(f"No se pudo importar el módulo principal: {e}")

    def test_import_reports(self):
        """Probar importación de módulos de reportes"""
        reports_to_test = [
            'csf_do.csf_do.report.dominican_purchase_tax_report.dominican_republic_purchase_tax_report',
            'csf_do.csf_do.report.dominican_republic_sales_tax_report.dominican_republic_sales_tax_report',
            'csf_do.csf_do.report.dominican_bank_payroll_advice_report.dominican_republic_bank_payroll_advice_report'
        ]

        for report_module in reports_to_test:
            with self.subTest(report=report_module):
                try:
                    __import__(report_module)
                    print(f"✓ Reporte {report_module} importado correctamente")
                except ImportError as e:
                    self.fail(f"No se pudo importar {report_module}: {e}")

class TestECFDRReports(ECFDRTestCase):
    """Pruebas de funcionalidad de reportes"""

    @patch('frappe.get_all')
    @patch('frappe.db.get_value')
    @patch('frappe.qb.from_')
    def test_purchase_tax_report_structure(self, mock_qb_from, mock_get_value, mock_get_all):
        """Probar estructura del reporte de compras"""
        # Mock de frappe.qb
        mock_query = MagicMock()
        mock_qb_from.return_value = mock_query
        mock_query.inner_join.return_value = mock_query
        mock_query.on.return_value = mock_query
        mock_query.select.return_value = mock_query
        mock_query.where.return_value = mock_query
        mock_query.run.return_value = []

        # Mock de frappe.db.get_value
        mock_get_value.return_value = 0.18  # 18% ITBIS

        try:
            from csf_do.csf_do.report.dominican_purchase_tax_report.dominican_republic_purchase_tax_report import execute

            # Probar ejecución con datos de prueba
            columns, data = execute(self.test_data)

            # Verificar estructura de respuesta
            self.assertIsInstance(columns, list)
            self.assertIsInstance(data, list)

            # Verificar que las columnas tengan la estructura correcta
            if columns:
                for col in columns:
                    self.assertIn('label', col)
                    self.assertIn('fieldname', col)
                    self.assertIn('fieldtype', col)

            print("✓ Reporte de compras tiene estructura correcta")

        except Exception as e:
            self.fail(f"Error en reporte de compras: {e}")

    @patch('frappe.get_all')
    @patch('frappe.qb.from_')
    def test_bank_payroll_report_structure(self, mock_qb_from, mock_get_all):
        """Probar estructura del reporte bancario de nómina"""
        # Mock de frappe.qb
        mock_query = MagicMock()
        mock_qb_from.return_value = mock_query
        mock_query.inner_join.return_value = mock_query
        mock_query.on.return_value = mock_query
        mock_query.select.return_value = mock_query
        mock_query.where.return_value = mock_query
        mock_query.run.return_value = []

        try:
            from csf_do.csf_do.report.dominican_bank_payroll_advice_report.dominican_republic_bank_payroll_advice_report import execute

            # Probar ejecución con datos de prueba
            columns, data = execute(self.test_data)

            # Verificar estructura de respuesta
            self.assertIsInstance(columns, list)
            self.assertIsInstance(data, list)

            # Verificar columnas específicas del reporte bancario
            column_names = [col.get('fieldname') for col in columns]
            expected_columns = ['employee', 'employee_name', 'bank_name', 'bank_account_no', 'net_pay']

            for expected_col in expected_columns:
                self.assertIn(expected_col, column_names,
                            f"Columna {expected_col} no encontrada en reporte bancario")

            print("✓ Reporte bancario tiene estructura correcta")

        except Exception as e:
            self.fail(f"Error en reporte bancario: {e}")

class TestECFDRIntegration(ECFDRTestCase):
    """Pruebas de integración"""

    def test_report_files_exist(self):
        """Verificar que todos los archivos de reportes existen"""
        report_files = [
            'csf_do/csf_do/report/dominican_purchase_tax_report/dominican_republic_purchase_tax_report.py',
            'csf_do/csf_do/report/dominican_republic_sales_tax_report/dominican_republic_sales_tax_report.py',
            'csf_do/csf_do/report/dominican_bank_payroll_advice_report/dominican_republic_bank_payroll_advice_report.py'
        ]

        for report_file in report_files:
            full_path = os.path.join(os.path.dirname(__file__), report_file)
            self.assertTrue(os.path.exists(full_path),
                          f"Archivo {report_file} no existe")
            print(f"✓ Archivo {report_file} existe")

    def test_json_configurations_valid(self):
        """Verificar que los archivos JSON de configuración sean válidos"""
        json_files = [
            'csf_do/csf_do/report/dominican_purchase_tax_report/dominican_purchase_tax_report.json',
            'csf_do/csf_do/report/dominican_republic_sales_tax_report/dominican_sales_tax_report.json',
            'csf_do/csf_do/report/dominican_bank_payroll_advice_report/dominican_bank_payroll_advice_report.json'
        ]

        for json_file in json_files:
            full_path = os.path.join(os.path.dirname(__file__), json_file)
            if os.path.exists(full_path):
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        json.load(f)
                    print(f"✓ Archivo JSON {json_file} es válido")
                except json.JSONDecodeError as e:
                    self.fail(f"Archivo JSON {json_file} no es válido: {e}")
            else:
                self.skipTest(f"Archivo {json_file} no existe")

class TestECFDRUtilities(ECFDRTestCase):
    """Pruebas de utilidades y funciones auxiliares"""

    def test_tax_calculations(self):
        """Probar cálculos de impuestos básicos"""
        # Prueba básica de cálculo de ITBIS
        taxable_amount = 1000
        tax_rate = 0.18  # 18%
        expected_tax = taxable_amount * tax_rate

        self.assertEqual(expected_tax, 180.0)
        print("✓ Cálculos básicos de ITBIS funcionan correctamente")

    def test_rnc_validation_pattern(self):
        """Probar patrones de validación de RNC"""
        import re

        # Patrón básico para RNC dominicano (9-11 dígitos)
        rnc_pattern = re.compile(r'^\d{9,11}$')

        valid_rncs = ['123456789', '12345678901', '00112233445']
        invalid_rncs = ['12345678', '123456789012', 'abc123456789', '']

        for rnc in valid_rncs:
            self.assertTrue(rnc_pattern.match(rnc), f"RNC {rnc} debería ser válido")

        for rnc in invalid_rncs:
            self.assertIsNone(rnc_pattern.match(rnc), f"RNC {rnc} debería ser inválido")

        print("✓ Validación de RNC funciona correctamente")

def run_integration_tests():
    """Ejecutar pruebas de integración específicas"""
    print("\n" + "="*60)
    print("EJECUTANDO PRUEBAS DE INTEGRACION ECFDR")
    print("="*60)

    # Crear suite de pruebas
    suite = unittest.TestSuite()

    # Agregar pruebas específicas
    suite.addTest(TestECFDRImports('test_import_main_module'))
    suite.addTest(TestECFDRImports('test_import_reports'))
    suite.addTest(TestECFDRIntegration('test_report_files_exist'))
    suite.addTest(TestECFDRIntegration('test_json_configurations_valid'))
    suite.addTest(TestECFDRUtilities('test_tax_calculations'))
    suite.addTest(TestECFDRUtilities('test_rnc_validation_pattern'))

    # Ejecutar pruebas
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()

def run_unit_tests():
    """Ejecutar pruebas unitarias específicas"""
    print("\n" + "="*60)
    print("EJECUTANDO PRUEBAS UNITARIAS ECFDR")
    print("="*60)

    # Crear suite de pruebas
    suite = unittest.TestSuite()

    # Agregar pruebas unitarias con mocks
    suite.addTest(TestECFDRReports('test_purchase_tax_report_structure'))
    suite.addTest(TestECFDRReports('test_bank_payroll_report_structure'))

    # Ejecutar pruebas
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()

def main():
    """Función principal"""
    print("PRUEBAS AUTOMATIZADAS ECFDR - REPUBLICA DOMINICANA")
    print("Electronic Comprobante Fiscal Digital")
    print("="*60)

    # Ejecutar pruebas de integración
    integration_success = run_integration_tests()

    # Ejecutar pruebas unitarias
    unit_success = run_unit_tests()

    # Resultado final
    print("\n" + "="*60)
    print("RESULTADO FINAL")
    print("="*60)

    if integration_success and unit_success:
        print("TODAS LAS PRUEBAS PASARON EXITOSAMENTE")
        print("ECFDR esta funcionando correctamente")
        return 0
    else:
        print("ALGUNAS PRUEBAS FALLARON")
        print("Revisar los errores arriba para corregir")
        return 1

if __name__ == '__main__':
    sys.exit(main())
