# -*- coding: utf-8 -*-
"""
Cliente unificado para API DGII
Maneja automáticamente el cambio entre simulador y API real
"""

import frappe
import requests
from typing import Dict, Any, Optional
from csf_do.csf_do.integrations.dgii_simulator import DGIISimulator


class DGIIClient:
    """
    Cliente unificado para interactuar con DGII.
    Cambia automáticamente entre simulador y API real según configuración.
    """
    
    def __init__(self):
        try:
            self.settings = frappe.get_single("DGII Configuration")
        except Exception:
            frappe.log_error("No se pudo cargar DGII Configuration")
            self.settings = None
        self.mode = self._get_mode()
        self.simulator = DGIISimulator()
        
    def _get_mode(self) -> str:
        """
        Obtiene el modo de operación
        Returns: 'simulator', 'test', 'production'
        """
        if not self.settings:
            return "simulator"
        return getattr(self.settings, "api_mode", "simulator")
    
    def _get_api_url(self) -> str:
        """Obtiene la URL base de la API según el modo"""
        if not self.settings:
            return "http://localhost:8000/dgii/api"
            
        if self.mode == "production":
            return self.settings.get("prod_base_url", "https://ecf.dgii.gov.do/api")
        elif self.mode == "test":
            return self.settings.get("cert_base_url", "https://ecf-test.dgii.gov.do/api")
        else:
            return "http://localhost:8000/dgii/api"  # Simulador
    
    def _get_credentials(self) -> Dict[str, str]:
        """Obtiene las credenciales de autenticación"""
        if not self.settings:
            return {
                "rnc": "",
                "usuario": "",
                "clave": ""
            }
        return {
            "rnc": self.settings.get("rnc_emisor", ""),
            "usuario": self.settings.get("client_id", ""),
            "clave": self.settings.get_password("client_secret", "")
        }
    
    # ==================== ENVÍO DE e-CF ====================
    
    def enviar_ecf(self, xml_content: str, ecf_type: str, ncf: str) -> Dict[str, Any]:
        """
        Envía un e-CF a DGII (simulador o API real)
        
        Args:
            xml_content: Contenido XML del e-CF firmado
            ecf_type: Tipo de e-CF (31, 32, 33, etc.)
            ncf: Número de Comprobante Fiscal
            
        Returns:
            Respuesta de DGII con track_id
        """
        if self.mode == "simulator":
            return self.simulator.enviar_ecf(xml_content, ecf_type, ncf)
        else:
            return self._enviar_ecf_real(xml_content, ecf_type, ncf)
    
    def _enviar_ecf_real(self, xml_content: str, ecf_type: str, ncf: str) -> Dict[str, Any]:
        """Envía e-CF a la API real de DGII"""
        url = f"{self._get_api_url()}/ecf/enviar"
        credentials = self._get_credentials()
        
        try:
            response = requests.post(
                url,
                json={
                    "xml": xml_content,
                    "tipo_ecf": ecf_type,
                    "ncf": ncf,
                    **credentials
                },
                timeout=30,
                headers={"Content-Type": "application/json"}
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "codigo": "408",
                "mensaje": "Timeout en la conexión con DGII"
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "codigo": "500",
                "mensaje": f"Error de conexión: {str(e)}"
            }
    
    # ==================== CONSULTA DE ESTADO ====================
    
    def consultar_estado(self, track_id: str) -> Dict[str, Any]:
        """
        Consulta el estado de un e-CF enviado
        
        Args:
            track_id: ID de seguimiento del e-CF
            
        Returns:
            Estado actual del e-CF
        """
        if self.mode == "simulator":
            return self.simulator.consultar_estado(track_id)
        else:
            return self._consultar_estado_real(track_id)
    
    def _consultar_estado_real(self, track_id: str) -> Dict[str, Any]:
        """Consulta estado en la API real de DGII"""
        url = f"{self._get_api_url()}/ecf/consultar"
        credentials = self._get_credentials()
        
        try:
            response = requests.get(
                url,
                params={
                    "track_id": track_id,
                    **credentials
                },
                timeout=15
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "codigo": "500",
                "mensaje": f"Error al consultar estado: {str(e)}"
            }
    
    # ==================== ACUSE DE RECIBO (ACECFAR) ====================
    
    def enviar_acuse_recibo(self, track_id: str, estado: str, motivo: str = "") -> Dict[str, Any]:
        """
        Envía acuse de recibo de un e-CF recibido
        
        Args:
            track_id: ID del e-CF recibido
            estado: ACEPTADO o RECHAZADO
            motivo: Motivo del rechazo (opcional)
            
        Returns:
            Confirmación del acuse
        """
        if self.mode == "simulator":
            return self.simulator.enviar_acuse_recibo(track_id, estado, motivo)
        else:
            return self._enviar_acuse_real(track_id, estado, motivo)
    
    def _enviar_acuse_real(self, track_id: str, estado: str, motivo: str) -> Dict[str, Any]:
        """Envía acuse de recibo a la API real"""
        url = f"{self._get_api_url()}/acecfar/enviar"
        credentials = self._get_credentials()
        
        try:
            response = requests.post(
                url,
                json={
                    "track_id": track_id,
                    "estado": estado,
                    "motivo": motivo,
                    **credentials
                },
                timeout=15
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "mensaje": f"Error al enviar acuse: {str(e)}"
            }
    
    # ==================== UTILIDADES ====================
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Prueba la conexión con DGII
        
        Returns:
            Resultado de la prueba
        """
        if self.mode == "simulator":
            return {
                "success": True,
                "modo": "simulator",
                "mensaje": "Simulador activo y funcionando"
            }
        
        url = f"{self._get_api_url()}/health"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            return {
                "success": True,
                "modo": self.mode,
                "mensaje": "Conexión exitosa con DGII",
                "url": url
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "modo": self.mode,
                "mensaje": f"Error de conexión: {str(e)}",
                "url": url
            }
    
    def get_info(self) -> Dict[str, Any]:
        """Obtiene información del cliente"""
        return {
            "modo": self.mode,
            "url_api": self._get_api_url(),
            "rnc_empresa": self.settings.get("company_rnc"),
            "simulador_activo": self.mode == "simulator"
        }


# ==================== API PÚBLICA ====================

def get_dgii_client() -> DGIIClient:
    """Obtiene una instancia del cliente DGII"""
    return DGIIClient()


@frappe.whitelist()
def enviar_ecf(xml_content: str, ecf_type: str, ncf: str) -> Dict[str, Any]:
    """API pública para enviar e-CF"""
    client = get_dgii_client()
    return client.enviar_ecf(xml_content, ecf_type, ncf)


@frappe.whitelist()
def consultar_estado(track_id: str) -> Dict[str, Any]:
    """API pública para consultar estado"""
    client = get_dgii_client()
    return client.consultar_estado(track_id)


@frappe.whitelist()
def test_connection() -> Dict[str, Any]:
    """API pública para probar conexión"""
    client = get_dgii_client()
    return client.test_connection()


@frappe.whitelist()
def get_client_info() -> Dict[str, Any]:
    """API pública para obtener info del cliente"""
    client = get_dgii_client()
    return client.get_info()
