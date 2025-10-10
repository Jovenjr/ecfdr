# -*- coding: utf-8 -*-
"""
DGII Simulator Config DocType
Configuración del simulador DGII desde la interfaz
"""

import frappe
from frappe.model.document import Document
from csf_do.csf_do.integrations.dgii_simulator import DGIISimulator


class DGIISimulatorConfig(Document):
    """Configuración del Simulador DGII"""
    
    def validate(self):
        """Validación antes de guardar"""
        self.update_mode_info()
    
    def update_mode_info(self):
        """Actualiza la información del modo actual"""
        simulator = DGIISimulator()
        self.mode_info = simulator.mode.upper()
    
    def on_update(self):
        """Después de actualizar"""
        if self.show_notifications:
            frappe.msgprint(
                f"Configuración del simulador actualizada. Modo: {self.mode_info}",
                indicator="green"
            )


@frappe.whitelist()
def test_simulator():
    """Prueba el simulador con un envío de prueba"""
    simulator = DGIISimulator()
    
    if not simulator.is_simulator_active():
        return {
            "success": False,
            "message": "El simulador no está activo"
        }
    
    # Envío de prueba
    result = simulator.enviar_ecf(
        xml_content="<test>XML de prueba</test>",
        ecf_type="31",
        ncf="B0100000001"
    )
    
    return {
        "success": result.get("success"),
        "message": "Prueba completada",
        "result": result
    }


@frappe.whitelist()
def reset_statistics():
    """Resetea las estadísticas del simulador"""
    doc = frappe.get_single("DGII Simulator Config")
    doc.total_ecf_enviados = 0
    doc.total_consultas = 0
    doc.ultimo_envio = None
    doc.ultimo_track_id = None
    doc.save()
    
    frappe.msgprint("Estadísticas reseteadas", indicator="blue")
    
    return {"success": True}


@frappe.whitelist()
def generate_test_ecf():
    """Genera un e-CF de prueba para testing"""
    simulator = DGIISimulator()
    
    xml = simulator.generar_ecf_proveedor(
        supplier_rnc="131793916",
        amount=11800.00
    )
    
    return {
        "success": True,
        "xml": xml,
        "message": "e-CF de prueba generado"
    }
