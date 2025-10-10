# -*- coding: utf-8 -*-
"""
Validador de Firma Digital para e-CF Recibidos
Valida la firma digital XMLDSig de e-CF de proveedores
"""

import frappe
from lxml import etree
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature
import base64
from typing import Dict, Optional, Tuple
from datetime import datetime


class SignatureValidator:
    """
    Validador de firma digital XMLDSig para e-CF.
    Valida certificados y firma digital según estándar DGII.
    """
    
    def __init__(self):
        self.namespaces = {
            'ds': 'http://www.w3.org/2000/09/xmldsig#',
            'ecf': 'http://dgii.gov.do/ecf/v1.0'
        }
    
    def validate_signature(self, xml_content: str) -> Dict[str, any]:
        """
        Valida la firma digital completa de un e-CF
        
        Args:
            xml_content: Contenido XML del e-CF
            
        Returns:
            Diccionario con resultado de validación
        """
        result = {
            'valid': False,
            'signature_present': False,
            'certificate_valid': False,
            'signature_verified': False,
            'certificate_info': {},
            'errors': []
        }
        
        try:
            tree = etree.fromstring(xml_content.encode('utf-8'))
            
            # 1. Verificar que existe firma
            signature_node = tree.find('.//ds:Signature', self.namespaces)
            if signature_node is None:
                result['errors'].append("No se encontró firma digital en el e-CF")
                return result
            
            result['signature_present'] = True
            
            # 2. Extraer certificado
            certificate = self._extract_certificate(signature_node)
            if not certificate:
                result['errors'].append("No se pudo extraer el certificado")
                return result
            
            # 3. Validar certificado
            cert_validation = self._validate_certificate(certificate)
            result['certificate_valid'] = cert_validation['valid']
            result['certificate_info'] = cert_validation['info']
            
            if not cert_validation['valid']:
                result['errors'].extend(cert_validation['errors'])
                # Continuar para verificar firma aunque certificado no sea válido
            
            # 4. Verificar firma digital
            signature_validation = self._verify_signature(tree, signature_node, certificate)
            result['signature_verified'] = signature_validation['valid']
            
            if not signature_validation['valid']:
                result['errors'].extend(signature_validation['errors'])
            
            # 5. Resultado final
            result['valid'] = (
                result['signature_present'] and
                result['certificate_valid'] and
                result['signature_verified']
            )
            
        except Exception as e:
            result['errors'].append(f"Error validando firma: {str(e)}")
            frappe.log_error(f"Error en validación de firma: {str(e)}", "Signature Validator")
        
        return result
    
    def _extract_certificate(self, signature_node) -> Optional[x509.Certificate]:
        """Extrae el certificado X.509 de la firma"""
        try:
            x509_cert_node = signature_node.find('.//ds:X509Certificate', self.namespaces)
            if x509_cert_node is None:
                return None
            
            cert_data = x509_cert_node.text.strip()
            cert_bytes = base64.b64decode(cert_data)
            
            certificate = x509.load_der_x509_certificate(cert_bytes, default_backend())
            return certificate
            
        except Exception as e:
            frappe.log_error(f"Error extrayendo certificado: {str(e)}", "Signature Validator")
            return None
    
    def _validate_certificate(self, certificate: x509.Certificate) -> Dict:
        """
        Valida el certificado X.509
        
        Validaciones:
        - Fechas de validez
        - Emisor
        - Propósito (firma digital)
        - No revocado (TODO: implementar CRL/OCSP)
        """
        result = {
            'valid': True,
            'errors': [],
            'info': {}
        }
        
        try:
            # Información del certificado
            subject = certificate.subject
            issuer = certificate.issuer
            
            result['info'] = {
                'subject': self._format_name(subject),
                'issuer': self._format_name(issuer),
                'serial_number': str(certificate.serial_number),
                'not_valid_before': certificate.not_valid_before.isoformat(),
                'not_valid_after': certificate.not_valid_after.isoformat(),
                'version': certificate.version.name
            }
            
            # 1. Validar fechas
            now = datetime.utcnow()
            if now < certificate.not_valid_before:
                result['valid'] = False
                result['errors'].append("Certificado aún no es válido")
            
            if now > certificate.not_valid_after:
                result['valid'] = False
                result['errors'].append("Certificado expirado")
            
            # 2. Validar que sea para firma digital
            try:
                key_usage = certificate.extensions.get_extension_for_oid(
                    x509.oid.ExtensionOID.KEY_USAGE
                ).value
                
                if not key_usage.digital_signature:
                    result['valid'] = False
                    result['errors'].append("Certificado no autorizado para firma digital")
            except x509.ExtensionNotFound:
                # Si no tiene extensión KEY_USAGE, asumir que es válido
                pass
            
            # 3. TODO: Validar cadena de confianza
            # Esto requiere tener los certificados raíz de DGII
            
            # 4. TODO: Verificar revocación (CRL/OCSP)
            # Esto requiere conexión a servicios de DGII
            
        except Exception as e:
            result['valid'] = False
            result['errors'].append(f"Error validando certificado: {str(e)}")
        
        return result
    
    def _verify_signature(self, tree, signature_node, certificate: x509.Certificate) -> Dict:
        """
        Verifica la firma digital del XML
        
        Proceso:
        1. Obtener SignedInfo canonicalizado
        2. Obtener SignatureValue
        3. Verificar con clave pública del certificado
        """
        result = {
            'valid': False,
            'errors': []
        }
        
        try:
            # 1. Obtener SignedInfo
            signed_info = signature_node.find('.//ds:SignedInfo', self.namespaces)
            if signed_info is None:
                result['errors'].append("No se encontró SignedInfo")
                return result
            
            # 2. Canonicalizar SignedInfo
            canonicalized = self._canonicalize(signed_info)
            
            # 3. Obtener SignatureValue
            sig_value_node = signature_node.find('.//ds:SignatureValue', self.namespaces)
            if sig_value_node is None:
                result['errors'].append("No se encontró SignatureValue")
                return result
            
            signature_value = base64.b64decode(sig_value_node.text.strip())
            
            # 4. Verificar firma con clave pública
            public_key = certificate.public_key()
            
            try:
                public_key.verify(
                    signature_value,
                    canonicalized,
                    padding.PKCS1v15(),
                    hashes.SHA256()
                )
                result['valid'] = True
                
            except InvalidSignature:
                result['errors'].append("Firma digital inválida")
            
        except Exception as e:
            result['errors'].append(f"Error verificando firma: {str(e)}")
            frappe.log_error(f"Error verificando firma: {str(e)}", "Signature Validator")
        
        return result
    
    def _canonicalize(self, element) -> bytes:
        """
        Canonicaliza un elemento XML según C14N
        """
        try:
            return etree.tostring(
                element,
                method='c14n',
                exclusive=False,
                with_comments=False
            )
        except Exception as e:
            frappe.log_error(f"Error canonicalizando: {str(e)}", "Signature Validator")
            raise
    
    def _format_name(self, name) -> str:
        """Formatea un nombre X.509 para display"""
        try:
            parts = []
            for attr in name:
                parts.append(f"{attr.oid._name}={attr.value}")
            return ", ".join(parts)
        except:
            return str(name)
    
    def extract_certificate_info(self, xml_content: str) -> Optional[Dict]:
        """
        Extrae información del certificado sin validar
        Útil para mostrar info antes de validar
        """
        try:
            tree = etree.fromstring(xml_content.encode('utf-8'))
            signature_node = tree.find('.//ds:Signature', self.namespaces)
            
            if signature_node is None:
                return None
            
            certificate = self._extract_certificate(signature_node)
            if not certificate:
                return None
            
            subject = certificate.subject
            issuer = certificate.issuer
            
            return {
                'subject': self._format_name(subject),
                'issuer': self._format_name(issuer),
                'serial_number': str(certificate.serial_number),
                'not_valid_before': certificate.not_valid_before.isoformat(),
                'not_valid_after': certificate.not_valid_after.isoformat(),
                'is_expired': datetime.utcnow() > certificate.not_valid_after
            }
            
        except Exception as e:
            frappe.log_error(f"Error extrayendo info de certificado: {str(e)}", "Signature Validator")
            return None


class SignatureValidatorSimulator:
    """
    Versión simulada del validador para desarrollo
    Acepta cualquier firma como válida
    """
    
    def validate_signature(self, xml_content: str) -> Dict:
        """Simula validación exitosa"""
        return {
            'valid': True,
            'signature_present': True,
            'certificate_valid': True,
            'signature_verified': True,
            'certificate_info': {
                'subject': 'CN=Proveedor Simulado, O=Empresa Test, C=DO',
                'issuer': 'CN=DGII CA, O=DGII, C=DO',
                'serial_number': '123456789',
                'not_valid_before': '2024-01-01T00:00:00',
                'not_valid_after': '2026-01-01T00:00:00',
                'version': 'v3'
            },
            'errors': [],
            'simulated': True
        }
    
    def extract_certificate_info(self, xml_content: str) -> Dict:
        """Simula extracción de info de certificado"""
        return {
            'subject': 'CN=Proveedor Simulado, O=Empresa Test, C=DO',
            'issuer': 'CN=DGII CA, O=DGII, C=DO',
            'serial_number': '123456789',
            'not_valid_before': '2024-01-01T00:00:00',
            'not_valid_after': '2026-01-01T00:00:00',
            'is_expired': False,
            'simulated': True
        }


# ==================== API PÚBLICA ====================

def validate_ecf_signature(xml_content: str, use_simulator: bool = None) -> Dict:
    """
    Valida la firma digital de un e-CF
    
    Args:
        xml_content: Contenido XML del e-CF
        use_simulator: Si usar simulador (None = auto-detectar)
        
    Returns:
        Resultado de validación
    """
    # Auto-detectar modo si no se especifica
    if use_simulator is None:
        settings = frappe.get_single("DGII Settings")
        use_simulator = getattr(settings, "api_mode", "simulator") == "simulator"
    
    if use_simulator:
        validator = SignatureValidatorSimulator()
    else:
        validator = SignatureValidator()
    
    return validator.validate_signature(xml_content)


def get_certificate_info(xml_content: str, use_simulator: bool = None) -> Optional[Dict]:
    """
    Extrae información del certificado de un e-CF
    
    Args:
        xml_content: Contenido XML del e-CF
        use_simulator: Si usar simulador (None = auto-detectar)
        
    Returns:
        Información del certificado o None
    """
    # Auto-detectar modo si no se especifica
    if use_simulator is None:
        settings = frappe.get_single("DGII Settings")
        use_simulator = getattr(settings, "api_mode", "simulator") == "simulator"
    
    if use_simulator:
        validator = SignatureValidatorSimulator()
    else:
        validator = SignatureValidator()
    
    return validator.extract_certificate_info(xml_content)
