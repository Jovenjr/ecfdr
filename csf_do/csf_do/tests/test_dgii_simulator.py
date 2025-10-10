# -*- coding: utf-8 -*-
"""
Tests para el Simulador DGII
"""

import unittest
import frappe
from csf_do.csf_do.integrations.dgii_simulator import DGIISimulator
from csf_do.csf_do.integrations.dgii_client import DGIIClient


class TestDGIISimulator(unittest.TestCase):
    """Tests del simulador DGII"""
    
    def setUp(self):
        """Setup antes de cada test"""
        self.simulator = DGIISimulator()
        
    def test_simulator_initialization(self):
        """Test: Inicialización del simulador"""
        self.assertIsNotNone(self.simulator)
        self.assertIn(self.simulator.mode, ["simulator", "test", "production"])
    
    def test_envio_exitoso(self):
        """Test: Envío exitoso de e-CF"""
        result = self.simulator.enviar_ecf(
            xml_content="<test>XML</test>",
            ecf_type="31",
            ncf="B0100000001"
        )
        
        self.assertTrue(result.get("success"))
        self.assertIn("track_id", result)
        self.assertEqual(result.get("ncf"), "B0100000001")
    
    def test_consulta_estado(self):
        """Test: Consulta de estado de e-CF"""
        # Primero enviar
        envio = self.simulator.enviar_ecf(
            xml_content="<test>XML</test>",
            ecf_type="31",
            ncf="B0100000002"
        )
        
        track_id = envio.get("track_id")
        
        # Luego consultar
        consulta = self.simulator.consultar_estado(track_id)
        
        self.assertTrue(consulta.get("success"))
        self.assertEqual(consulta.get("track_id"), track_id)
        self.assertIn(consulta.get("estado"), ["RECIBIDO", "EN_PROCESO", "ACEPTADO", "RECHAZADO"])
    
    def test_consulta_track_id_inexistente(self):
        """Test: Consulta con track_id que no existe"""
        result = self.simulator.consultar_estado("track-id-falso-12345")
        
        self.assertFalse(result.get("success"))
        self.assertEqual(result.get("codigo"), "404")
    
    def test_generar_ecf_proveedor(self):
        """Test: Generación de e-CF de proveedor"""
        xml = self.simulator.generar_ecf_proveedor(
            supplier_rnc="131793916",
            amount=11800.00
        )
        
        self.assertIsNotNone(xml)
        self.assertIn("<?xml", xml)
        self.assertIn("131793916", xml)
        self.assertIn("11800", xml)
    
    def test_acuse_recibo(self):
        """Test: Envío de acuse de recibo"""
        result = self.simulator.enviar_acuse_recibo(
            track_id="test-track-123",
            estado="ACEPTADO"
        )
        
        self.assertTrue(result.get("success"))
        self.assertEqual(result.get("estado_acuse"), "ACEPTADO")
    
    def test_generate_ncf(self):
        """Test: Generación de NCF"""
        ncf = self.simulator._generate_ncf("B01")
        
        self.assertIsNotNone(ncf)
        self.assertTrue(ncf.startswith("B01"))
        self.assertEqual(len(ncf), 11)  # B01 + 8 dígitos


class TestDGIIClient(unittest.TestCase):
    """Tests del cliente unificado DGII"""
    
    def setUp(self):
        """Setup antes de cada test"""
        self.client = DGIIClient()
    
    def test_client_initialization(self):
        """Test: Inicialización del cliente"""
        self.assertIsNotNone(self.client)
        self.assertIsNotNone(self.client.mode)
    
    def test_get_info(self):
        """Test: Obtener información del cliente"""
        info = self.client.get_info()
        
        self.assertIn("modo", info)
        self.assertIn("url_api", info)
        self.assertIn("simulador_activo", info)
    
    def test_envio_con_cliente(self):
        """Test: Envío usando el cliente unificado"""
        result = self.client.enviar_ecf(
            xml_content="<test>XML</test>",
            ecf_type="31",
            ncf="B0100000003"
        )
        
        # Si está en modo simulador, debe funcionar
        if self.client.mode == "simulator":
            self.assertTrue(result.get("success"))
            self.assertIn("track_id", result)


def run_tests():
    """Ejecuta todos los tests del simulador"""
    suite = unittest.TestSuite()
    
    # Agregar tests
    suite.addTest(unittest.makeSuite(TestDGIISimulator))
    suite.addTest(unittest.makeSuite(TestDGIIClient))
    
    # Ejecutar
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result


if __name__ == "__main__":
    unittest.main()
