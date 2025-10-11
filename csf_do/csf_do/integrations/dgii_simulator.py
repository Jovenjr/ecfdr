# -*- coding: utf-8 -*-
"""
Simulador de API DGII para desarrollo y testing
Replica el comportamiento esperado de la API real de DGII
"""

import frappe
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import random


class DGIISimulator:
    """
    Simulador de la API DGII para desarrollo y testing.
    Permite probar toda la funcionalidad sin conexión real a DGII.
    """
    
    def __init__(self):
        self.base_url = "http://localhost:8000/dgii/api"  # URL del simulador
        self.mode = self._get_mode()
        
    def _get_mode(self) -> str:
        """Obtiene el modo de operación desde configuración"""
        try:
            settings = frappe.get_single("DGII Configuration")
            return getattr(settings, "api_mode", "simulator")  # simulator, test, production
        except Exception:
            return "simulator"  # Por defecto si no existe configuración
    
    def is_simulator_active(self) -> bool:
        """Verifica si el simulador está activo"""
        return self.mode == "simulator"
    
    # ==================== ENVÍO DE e-CF ====================
    
    def enviar_ecf(self, xml_content: str, ecf_type: str, ncf: str) -> Dict[str, Any]:
        """
        Simula el envío de un e-CF a DGII
        
        Args:
            xml_content: Contenido XML del e-CF
            ecf_type: Tipo de e-CF (31, 32, 33, etc.)
            ncf: Número de Comprobante Fiscal
            
        Returns:
            Respuesta simulada de DGII
        """
        # Log de inicio
        frappe.logger().info(f"[DGII Simulator] Iniciando envío e-CF - NCF: {ncf}, Tipo: {ecf_type}")
        
        if not self.is_simulator_active():
            frappe.logger().error("[DGII Simulator] Simulador no está activo")
            raise Exception("Simulador no está activo. Use la API real.")
        
        # Simular diferentes escenarios basados en configuración
        scenario = self._get_scenario("envio")
        frappe.logger().info(f"[DGII Simulator] Escenario configurado: {scenario}")
        
        result = None
        if scenario == "success":
            result = self._simulate_success_response(ncf)
        elif scenario == "validation_error":
            result = self._simulate_validation_error()
        elif scenario == "timeout":
            result = self._simulate_timeout()
        elif scenario == "server_error":
            result = self._simulate_server_error()
        else:
            # Por defecto, éxito
            result = self._simulate_success_response(ncf)
        
        # Log del resultado
        status = "ÉXITO" if result.get("success") else "ERROR"
        frappe.logger().info(f"[DGII Simulator] Resultado: {status} - Código: {result.get('codigo')}")
        
        return result
    
    def _simulate_success_response(self, ncf: str) -> Dict[str, Any]:
        """Simula una respuesta exitosa de DGII"""
        track_id = str(uuid.uuid4())
        
        frappe.logger().info(f"[DGII Simulator] Generando respuesta exitosa - Track ID: {track_id}")
        
        # Guardar en caché para consultas posteriores
        self._save_to_cache(track_id, {
            "ncf": ncf,
            "status": "ACEPTADO",
            "fecha_recepcion": datetime.now().isoformat(),
            "track_id": track_id
        })
        
        return {
            "success": True,
            "track_id": track_id,
            "codigo": "200",
            "mensaje": "e-CF recibido correctamente",
            "fecha_recepcion": datetime.now().isoformat(),
            "ncf": ncf
        }
    
    def _simulate_validation_error(self) -> Dict[str, Any]:
        """Simula un error de validación con códigos DGII oficiales"""
        # Códigos de error simulados basados en especificación DGII
        errores_dgii = [
            {
                "codigo": "DGII_001",
                "mensaje": "RNC del emisor no está registrado en DGII",
                "campo": "RNCEmisor"
            },
            {
                "codigo": "DGII_002",
                "mensaje": "NCF no corresponde a serie autorizada",
                "campo": "eNCF"
            },
            {
                "codigo": "DGII_003",
                "mensaje": "Firma digital inválida o certificado expirado",
                "campo": "Signature"
            },
            {
                "codigo": "DGII_004",
                "mensaje": "NCF ya fue utilizado anteriormente",
                "campo": "eNCF"
            },
            {
                "codigo": "DGII_005",
                "mensaje": "Secuencia de NCF agotada o fuera de rango",
                "campo": "eNCF"
            },
            {
                "codigo": "DGII_006",
                "mensaje": "Fecha de emisión fuera del rango permitido (máximo 30 días)",
                "campo": "FechaEmision"
            },
            {
                "codigo": "DGII_007",
                "mensaje": "Monto total no coincide con suma de ítems + impuestos",
                "campo": "MontoTotal"
            },
            {
                "codigo": "DGII_008",
                "mensaje": "ITBIS calculado incorrectamente",
                "campo": "ITBIS1"
            },
            {
                "codigo": "DGII_009",
                "mensaje": "RNC del comprador no es válido",
                "campo": "RNCComprador"
            },
            {
                "codigo": "DGII_010",
                "mensaje": "Tipo de e-CF no corresponde con el NCF utilizado",
                "campo": "TipoeCF"
            }
        ]
        
        error_seleccionado = random.choice(errores_dgii)
        
        return {
            "success": False,
            "codigo": "400",
            "codigoError": error_seleccionado["codigo"],
            "mensaje": "Error de validación del e-CF",
            "errores": [error_seleccionado],
            "fecha_recepcion": datetime.now().isoformat()
        }
    
    def _simulate_timeout(self) -> Dict[str, Any]:
        """Simula un timeout"""
        return {
            "success": False,
            "codigo": "408",
            "mensaje": "Timeout en la conexión con DGII",
            "fecha_recepcion": datetime.now().isoformat()
        }
    
    def _simulate_server_error(self) -> Dict[str, Any]:
        """Simula un error del servidor DGII"""
        return {
            "success": False,
            "codigo": "500",
            "mensaje": "Error interno del servidor DGII. Intente más tarde.",
            "fecha_recepcion": datetime.now().isoformat()
        }
    
    # ==================== CONSULTA DE ESTADO ====================
    
    def consultar_estado(self, track_id: str) -> Dict[str, Any]:
        """
        Simula la consulta de estado de un e-CF enviado
        
        Args:
            track_id: ID de seguimiento del e-CF
            
        Returns:
            Estado actual del e-CF
        """
        frappe.logger().info(f"[DGII Simulator] Consultando estado - Track ID: {track_id}")
        
        if not self.is_simulator_active():
            frappe.logger().error("[DGII Simulator] Simulador no está activo")
            raise Exception("Simulador no está activo. Use la API real.")
        
        # Buscar en caché
        cached_data = self._get_from_cache(track_id)
        
        if not cached_data:
            frappe.logger().warning(f"[DGII Simulator] Track ID no encontrado: {track_id}")
            return {
                "success": False,
                "codigo": "404",
                "mensaje": "TrackID no encontrado"
            }
        
        # Simular progresión de estados
        status = self._simulate_status_progression(cached_data)
        
        frappe.logger().info(f"[DGII Simulator] Estado actual: {status}")
        
        return {
            "success": True,
            "track_id": track_id,
            "ncf": cached_data.get("ncf"),
            "estado": status,
            "fecha_recepcion": cached_data.get("fecha_recepcion"),
            "fecha_procesamiento": datetime.now().isoformat(),
            "mensaje": self._get_status_message(status)
        }
    
    def _simulate_status_progression(self, cached_data: Dict) -> str:
        """
        Simula la progresión de estados de un e-CF
        RECIBIDO -> EN_PROCESO -> ACEPTADO/RECHAZADO
        """
        fecha_recepcion = datetime.fromisoformat(cached_data.get("fecha_recepcion"))
        tiempo_transcurrido = (datetime.now() - fecha_recepcion).seconds
        
        # Simular progresión temporal
        if tiempo_transcurrido < 10:
            return "RECIBIDO"
        elif tiempo_transcurrido < 30:
            return "EN_PROCESO"
        else:
            # 95% aceptado, 5% rechazado
            return "ACEPTADO" if random.random() > 0.05 else "RECHAZADO"
    
    def _get_status_message(self, status: str) -> str:
        """Obtiene mensaje descriptivo del estado"""
        messages = {
            "RECIBIDO": "e-CF recibido, en cola de procesamiento",
            "EN_PROCESO": "e-CF en proceso de validación",
            "ACEPTADO": "e-CF aceptado por DGII",
            "RECHAZADO": "e-CF rechazado. Revisar errores de validación"
        }
        return messages.get(status, "Estado desconocido")
    
    # ==================== RECEPCIÓN DE e-CF (ACECFAR) ====================
    
    def generar_ecf_proveedor(self, supplier_rnc: str, amount: float) -> str:
        """
        Genera un e-CF simulado de un proveedor (para testing de ACECFAR)
        
        Args:
            supplier_rnc: RNC del proveedor
            amount: Monto de la factura
            
        Returns:
            XML del e-CF simulado
        """
        ncf = self._generate_ncf("B01")
        
        xml_template = f"""<?xml version="1.0" encoding="UTF-8"?>
<ECF xmlns="http://dgii.gov.do/ecf/v1.0">
    <Encabezado>
        <Version>1.0</Version>
        <IdDoc>
            <TipoeCF>31</TipoeCF>
            <eNCF>{ncf}</eNCF>
            <FechaEmision>{datetime.now().strftime('%Y-%m-%d')}</FechaEmision>
        </IdDoc>
        <Emisor>
            <RNCEmisor>{supplier_rnc}</RNCEmisor>
            <RazonSocialEmisor>Proveedor Simulado S.A.</RazonSocialEmisor>
        </Emisor>
        <Comprador>
            <RNCComprador>{{COMPANY_RNC}}</RNCComprador>
            <RazonSocialComprador>{{COMPANY_NAME}}</RazonSocialComprador>
        </Comprador>
        <Totales>
            <MontoTotal>{amount}</MontoTotal>
            <MontoGravadoTotal>{amount / 1.18:.2f}</MontoGravadoTotal>
            <ITBIS1>{amount - (amount / 1.18):.2f}</ITBIS1>
        </Totales>
    </Encabezado>
    <DetallesItems>
        <Item>
            <NumeroLinea>1</NumeroLinea>
            <DescripcionItem>Producto/Servicio Simulado</DescripcionItem>
            <CantidadItem>1</CantidadItem>
            <PrecioUnitarioItem>{amount / 1.18:.2f}</PrecioUnitarioItem>
            <MontoItem>{amount / 1.18:.2f}</MontoItem>
        </Item>
    </DetallesItems>
    <Signature xmlns="http://www.w3.org/2000/09/xmldsig#">
        <SignedInfo>
            <CanonicalizationMethod Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315"/>
            <SignatureMethod Algorithm="http://www.w3.org/2001/04/xmldsig-more#rsa-sha256"/>
        </SignedInfo>
        <SignatureValue>SIMULADO_SIGNATURE_VALUE_BASE64</SignatureValue>
    </Signature>
</ECF>"""
        
        return xml_template
    
    def enviar_acuse_recibo(self, track_id: str, estado: str, motivo: str = "") -> Dict[str, Any]:
        """
        Simula el envío de acuse de recibo (ACECFAR)
        
        Args:
            track_id: ID del e-CF recibido
            estado: ACEPTADO o RECHAZADO
            motivo: Motivo del rechazo (si aplica)
            
        Returns:
            Confirmación del acuse
        """
        return {
            "success": True,
            "track_id": track_id,
            "estado_acuse": estado,
            "fecha_acuse": datetime.now().isoformat(),
            "mensaje": f"Acuse de recibo {estado.lower()} registrado correctamente"
        }
    
    # ==================== UTILIDADES ====================
    
    def _get_scenario(self, operation: str) -> str:
        """
        Obtiene el escenario configurado para una operación
        Permite simular diferentes comportamientos
        """
        try:
            # Buscar en DGII Simulator Config si existe
            config = frappe.get_single("DGII Simulator Config")
            scenario_field = f"scenario_{operation}"
            return getattr(config, scenario_field, "success")
        except Exception:
            # Si no existe configuración, retornar éxito por defecto
            return "success"
    
    def _save_to_cache(self, track_id: str, data: Dict):
        """Guarda datos en caché para consultas posteriores"""
        cache_key = f"dgii_simulator_{track_id}"
        frappe.cache().set_value(cache_key, json.dumps(data), expires_in_sec=86400)  # 24 horas
    
    def _get_from_cache(self, track_id: str) -> Optional[Dict]:
        """Obtiene datos de caché"""
        cache_key = f"dgii_simulator_{track_id}"
        cached = frappe.cache().get_value(cache_key)
        
        if cached:
            return json.loads(cached)
        return None
    
    def _generate_ncf(self, serie: str) -> str:
        """Genera un NCF simulado"""
        sequence = random.randint(1, 999999)
        return f"{serie}{sequence:08d}"
    
    # ==================== CONFIGURACIÓN ====================
    
    def set_scenario(self, operation: str, scenario: str):
        """
        Configura el escenario para una operación
        
        Args:
            operation: envio, consulta, acuse
            scenario: success, validation_error, timeout, server_error
        """
        try:
            config = frappe.get_single("DGII Simulator Config")
            scenario_field = f"scenario_{operation}"
            config.set(scenario_field, scenario)
            config.save()
            
            frappe.msgprint(f"Escenario '{scenario}' configurado para '{operation}'")
        except Exception as e:
            frappe.log_error(f"Error configurando escenario: {str(e)}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas del simulador"""
        try:
            # Contar items en caché del simulador
            cache_pattern = "dgii_simulator_*"
            cached_items = 0
            
            # Intentar contar items (implementación básica)
            # En producción, esto podría consultar Redis directamente
            
            return {
                "modo": self.mode,
                "activo": self.is_simulator_active(),
                "ecf_enviados": cached_items,
                "url_base": self.base_url,
                "version": "1.0.0"
            }
        except Exception as e:
            frappe.log_error(f"Error obteniendo estadísticas: {str(e)}")
            return {
                "modo": self.mode,
                "activo": self.is_simulator_active(),
                "error": str(e)
            }
    
    def _count_cached_items(self) -> int:
        """Cuenta items en caché del simulador"""
        # Implementación básica
        return 0  # TODO: Implementar conteo real
    
    def reset_simulator(self):
        """
        Reinicia el simulador limpiando toda la caché
        Útil para testing y desarrollo
        """
        try:
            # Limpiar caché del simulador
            # Buscar todas las keys que empiecen con dgii_simulator_
            cache = frappe.cache()
            
            # Nota: Frappe cache no tiene método para listar keys
            # Alternativa: guardar lista de track_ids
            
            frappe.msgprint("Simulador reiniciado correctamente")
            frappe.log_error("Simulador DGII reiniciado", "DGII Simulator")
            
            return {
                "success": True,
                "mensaje": "Simulador reiniciado, caché limpiada"
            }
        except Exception as e:
            frappe.log_error(f"Error reiniciando simulador: {str(e)}")
            return {
                "success": False,
                "mensaje": f"Error: {str(e)}"
            }
    
    def get_error_catalog(self) -> Dict[str, Any]:
        """
        Retorna el catálogo completo de códigos de error DGII simulados
        """
        return {
            "DGII_001": {
                "mensaje": "RNC del emisor no está registrado en DGII",
                "campo": "RNCEmisor",
                "severidad": "ERROR",
                "solucion": "Verificar que el RNC esté registrado y activo en DGII"
            },
            "DGII_002": {
                "mensaje": "NCF no corresponde a serie autorizada",
                "campo": "eNCF",
                "severidad": "ERROR",
                "solucion": "Usar NCF de serie autorizada por DGII"
            },
            "DGII_003": {
                "mensaje": "Firma digital inválida o certificado expirado",
                "campo": "Signature",
                "severidad": "ERROR",
                "solucion": "Renovar certificado digital o verificar configuración de firma"
            },
            "DGII_004": {
                "mensaje": "NCF ya fue utilizado anteriormente",
                "campo": "eNCF",
                "severidad": "ERROR",
                "solucion": "Usar siguiente NCF de la secuencia"
            },
            "DGII_005": {
                "mensaje": "Secuencia de NCF agotada o fuera de rango",
                "campo": "eNCF",
                "severidad": "ERROR",
                "solucion": "Solicitar nueva serie de NCF a DGII"
            },
            "DGII_006": {
                "mensaje": "Fecha de emisión fuera del rango permitido (máximo 30 días)",
                "campo": "FechaEmision",
                "severidad": "WARNING",
                "solucion": "Ajustar fecha de emisión dentro del rango permitido"
            },
            "DGII_007": {
                "mensaje": "Monto total no coincide con suma de ítems + impuestos",
                "campo": "MontoTotal",
                "severidad": "ERROR",
                "solucion": "Verificar cálculos de totales e impuestos"
            },
            "DGII_008": {
                "mensaje": "ITBIS calculado incorrectamente",
                "campo": "ITBIS1",
                "severidad": "ERROR",
                "solucion": "Recalcular ITBIS (18% sobre monto gravado)"
            },
            "DGII_009": {
                "mensaje": "RNC del comprador no es válido",
                "campo": "RNCComprador",
                "severidad": "WARNING",
                "solucion": "Verificar formato RNC (9 u 11 dígitos)"
            },
            "DGII_010": {
                "mensaje": "Tipo de e-CF no corresponde con el NCF utilizado",
                "campo": "TipoeCF",
                "severidad": "ERROR",
                "solucion": "Usar tipo de e-CF correcto según serie NCF"
            },
            "DGII_011": {
                "mensaje": "XML no cumple con esquema e-CF 4.3",
                "campo": "XML",
                "severidad": "ERROR",
                "solucion": "Validar XML contra esquema XSD oficial"
            },
            "DGII_012": {
                "mensaje": "Código de seguridad inválido",
                "campo": "CodigoSeguridad",
                "severidad": "ERROR",
                "solucion": "Regenerar código de seguridad desde firma digital"
            }
        }
        # Esta es una implementación básica, se puede mejorar
        
        return {
            "modo": self.mode,
            "activo": self.is_simulator_active(),
            "ecf_enviados": self._count_cached_items(),
            "url_base": self.base_url
        }
    
    def _count_cached_items(self) -> int:
        """Cuenta items en caché del simulador"""
        # Implementación básica
        return 0  # TODO: Implementar conteo real


# ==================== API PÚBLICA ====================

def enviar_ecf_simulado(xml_content: str, ecf_type: str, ncf: str) -> Dict[str, Any]:
    """
    Función pública para enviar e-CF usando el simulador
    """
    simulator = DGIISimulator()
    return simulator.enviar_ecf(xml_content, ecf_type, ncf)


def consultar_estado_simulado(track_id: str) -> Dict[str, Any]:
    """
    Función pública para consultar estado usando el simulador
    """
    simulator = DGIISimulator()
    return simulator.consultar_estado(track_id)


def generar_ecf_proveedor_simulado(supplier_rnc: str, amount: float) -> str:
    """
    Función pública para generar e-CF de proveedor simulado
    """
    simulator = DGIISimulator()
    return simulator.generar_ecf_proveedor(supplier_rnc, amount)


def configurar_escenario(operation: str, scenario: str):
    """
    Función pública para configurar escenarios de simulación
    """
    simulator = DGIISimulator()
    simulator.set_scenario(operation, scenario)


def reiniciar_simulador():
    """
    Función pública para reiniciar el simulador
    """
    simulator = DGIISimulator()
    return simulator.reset_simulator()


def obtener_catalogo_errores():
    """
    Función pública para obtener catálogo de errores DGII
    """
    simulator = DGIISimulator()
    return simulator.get_error_catalog()


def obtener_estadisticas_simulador():
    """
    Función pública para obtener estadísticas del simulador
    """
    simulator = DGIISimulator()
    return simulator.get_statistics()

