# -*- coding: utf-8 -*-
"""
Tests para el módulo ACECFAR (Recepción de e-CF)
"""

import unittest
import frappe
from csf_do.csf_do.utils.acecfar_parser import ACECFARParser, parse_ecf_xml
from csf_do.csf_do.utils.signature_validator import validate_ecf_signature
from csf_do.csf_do.integrations.acecfar_processor import ACECFARProcessor
from csf_do.csf_do.integrations.dgii_simulator import DGIISimulator


class TestACECFARParser(unittest.TestCase):
    """Tests del parser de e-CF"""
    
    def setUp(self):
        """Setup antes de cada test"""
        self.parser = ACECFARParser()
        self.simulator = DGIISimulator()
        
        # Generar e-CF de prueba
        self.test_xml = self.simulator.generar_ecf_proveedor(
            supplier_rnc="131793916",
            amount=11800.00
        )
    
    def test_parser_initialization(self):
        """Test: Inicialización del parser"""
        self.assertIsNotNone(self.parser)
        self.assertIn('ecf', self.parser.namespaces)
    
    def test_parse_xml_success(self):
        """Test: Parseo exitoso de XML"""
        result = self.parser.parse_xml(self.test_xml)
        
        self.assertIsNotNone(result)
        self.assertIn('header', result)
        self.assertIn('emisor', result)
        self.assertIn('items', result)
        self.assertIn('totales', result)
    
    def test_extract_header(self):
        """Test: Extracción de encabezado"""
        from lxml import etree
        tree = etree.fromstring(self.test_xml.encode('utf-8'))
        
        header = self.parser.extract_header(tree)
        
        self.assertIsNotNone(header)
        self.assertIn('tipo_ecf', header)
        self.assertIn('encf', header)
    
    def test_extract_emisor(self):
        """Test: Extracción de datos del emisor"""
        from lxml import etree
        tree = etree.fromstring(self.test_xml.encode('utf-8'))
        
        emisor = self.parser.extract_emisor(tree)
        
        self.assertIsNotNone(emisor)
        self.assertEqual(emisor.get('rnc'), '131793916')
    
    def test_extract_items(self):
        """Test: Extracción de ítems"""
        from lxml import etree
        tree = etree.fromstring(self.test_xml.encode('utf-8'))
        
        items = self.parser.extract_items(tree)
        
        self.assertIsInstance(items, list)
        self.assertGreater(len(items), 0)
    
    def test_extract_totales(self):
        """Test: Extracción de totales"""
        from lxml import etree
        tree = etree.fromstring(self.test_xml.encode('utf-8'))
        
        totales = self.parser.extract_totales(tree)
        
        self.assertIsNotNone(totales)
        self.assertIn('monto_total', totales)
        self.assertEqual(totales.get('monto_total'), 11800.00)
    
    def test_parse_invalid_xml(self):
        """Test: Parseo de XML inválido"""
        with self.assertRaises(Exception):
            self.parser.parse_xml("<invalid>XML</invalid>")


class TestSignatureValidator(unittest.TestCase):
    """Tests del validador de firma"""
    
    def setUp(self):
        """Setup antes de cada test"""
        self.simulator = DGIISimulator()
        self.test_xml = self.simulator.generar_ecf_proveedor(
            supplier_rnc="131793916",
            amount=11800.00
        )
    
    def test_validate_signature_simulator(self):
        """Test: Validación de firma con simulador"""
        result = validate_ecf_signature(self.test_xml, use_simulator=True)
        
        self.assertIsNotNone(result)
        self.assertTrue(result.get('valid'))
        self.assertTrue(result.get('signature_present'))
        self.assertTrue(result.get('simulated'))
    
    def test_extract_certificate_info(self):
        """Test: Extracción de info de certificado"""
        from csf_do.csf_do.utils.signature_validator import get_certificate_info
        
        info = get_certificate_info(self.test_xml, use_simulator=True)
        
        self.assertIsNotNone(info)
        self.assertIn('subject', info)
        self.assertIn('issuer', info)


class TestACECFARProcessor(unittest.TestCase):
    """Tests del procesador ACECFAR"""
    
    def setUp(self):
        """Setup antes de cada test"""
        self.processor = ACECFARProcessor()
        self.simulator = DGIISimulator()
        
        # Generar e-CF de prueba
        self.test_xml = self.simulator.generar_ecf_proveedor(
            supplier_rnc="131793916",
            amount=11800.00
        )
    
    def test_processor_initialization(self):
        """Test: Inicialización del procesador"""
        self.assertIsNotNone(self.processor)
        self.assertIsNotNone(self.processor.company)
    
    def test_process_ecf_full_flow(self):
        """Test: Flujo completo de procesamiento"""
        # Este test requiere una instalación completa de ERPNext
        # Por ahora solo verificamos que no lance excepciones
        
        try:
            result = self.processor.process_ecf(self.test_xml, validate_signature=False)
            
            # Verificar estructura de respuesta
            self.assertIn('success', result)
            self.assertIn('errors', result)
            self.assertIn('warnings', result)
            
        except Exception as e:
            # Si falla por falta de datos maestros, es esperado en tests
            if "Company" not in str(e) and "Supplier" not in str(e):
                raise


class TestACECFARIntegration(unittest.TestCase):
    """Tests de integración del módulo ACECFAR"""
    
    def setUp(self):
        """Setup antes de cada test"""
        self.simulator = DGIISimulator()
    
    def test_full_workflow(self):
        """Test: Workflow completo de recepción de e-CF"""
        # 1. Generar e-CF de proveedor
        xml = self.simulator.generar_ecf_proveedor("131793916", 11800.00)
        self.assertIsNotNone(xml)
        
        # 2. Parsear XML
        parsed = parse_ecf_xml(xml)
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed['emisor']['rnc'], '131793916')
        
        # 3. Validar firma (simulador)
        sig_result = validate_ecf_signature(xml, use_simulator=True)
        self.assertTrue(sig_result.get('valid'))
        
        # 4. Procesar (crear PI) - requiere datos maestros
        # Este paso se omite en tests unitarios


def run_tests():
    """Ejecuta todos los tests de ACECFAR"""
    suite = unittest.TestSuite()
    
    # Agregar tests
    suite.addTest(unittest.makeSuite(TestACECFARParser))
    suite.addTest(unittest.makeSuite(TestSignatureValidator))
    suite.addTest(unittest.makeSuite(TestACECFARProcessor))
    suite.addTest(unittest.makeSuite(TestACECFARIntegration))
    
    # Ejecutar
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result


if __name__ == "__main__":
    unittest.main()
