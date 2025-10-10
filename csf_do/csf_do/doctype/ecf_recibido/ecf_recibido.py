# -*- coding: utf-8 -*-
"""
e-CF Recibido DocType
Registro de e-CF recibidos de proveedores
"""

import frappe
from frappe.model.document import Document
from frappe import _


class eCFRecibido(Document):
    """e-CF Recibido de proveedores"""
    
    def validate(self):
        """Validación antes de guardar"""
        self.validate_encf()
        self.validate_amounts()
    
    def validate_encf(self):
        """Valida el formato del e-NCF"""
        if not self.encf:
            frappe.throw(_("e-NCF es requerido"))
        
        # Validar que no exista duplicado
        if self.is_new():
            existing = frappe.db.exists('e-CF Recibido', {'encf': self.encf, 'name': ['!=', self.name]})
            if existing:
                frappe.throw(_("Ya existe un e-CF con este número: {0}").format(self.encf))
    
    def validate_amounts(self):
        """Valida los montos"""
        if self.monto_total <= 0:
            frappe.throw(_("Monto total debe ser mayor a cero"))
    
    def on_update(self):
        """Después de actualizar"""
        # Si cambió a Procesado, actualizar fecha
        if self.status == "Procesado" and not self.fecha_procesamiento:
            self.db_set('fecha_procesamiento', frappe.utils.now())
            self.db_set('procesado_por', frappe.session.user)


@frappe.whitelist()
def procesar_ecf(name: str):
    """
    Procesa un e-CF Recibido creando Purchase Invoice
    
    Args:
        name: Nombre del documento e-CF Recibido
    """
    from csf_do.csf_do.integrations.acecfar_processor import reprocess_ecf_recibido
    
    result = reprocess_ecf_recibido(name)
    
    if result.get('success'):
        frappe.msgprint(
            _("Purchase Invoice {0} creada exitosamente").format(result.get('purchase_invoice')),
            indicator="green"
        )
    else:
        frappe.msgprint(
            _("Error procesando e-CF: {0}").format(", ".join(result.get('errors', []))),
            indicator="red"
        )
    
    return result


@frappe.whitelist()
def enviar_acuse(name: str, estado: str, motivo: str = ""):
    """
    Envía acuse de recibo a DGII
    
    Args:
        name: Nombre del documento e-CF Recibido
        estado: ACEPTADO o RECHAZADO
        motivo: Motivo del rechazo (si aplica)
    """
    from csf_do.csf_do.integrations.dgii_client import get_dgii_client
    
    doc = frappe.get_doc('e-CF Recibido', name)
    
    # Generar track_id temporal (en producción vendría del XML)
    track_id = f"ACE-{doc.encf}"
    
    # Enviar acuse
    client = get_dgii_client()
    result = client.enviar_acuse_recibo(track_id, estado, motivo)
    
    if result.get('success'):
        doc.acuse_enviado = 1
        doc.fecha_acuse = frappe.utils.now()
        doc.estado_acuse = estado
        doc.track_id_acuse = result.get('track_id', track_id)
        doc.save()
        
        frappe.msgprint(
            _("Acuse de recibo enviado exitosamente"),
            indicator="green"
        )
    else:
        frappe.msgprint(
            _("Error enviando acuse: {0}").format(result.get('mensaje')),
            indicator="red"
        )
    
    return result


@frappe.whitelist()
def validar_firma(name: str):
    """
    Valida la firma digital de un e-CF Recibido
    
    Args:
        name: Nombre del documento e-CF Recibido
    """
    from csf_do.csf_do.utils.signature_validator import validate_ecf_signature
    
    doc = frappe.get_doc('e-CF Recibido', name)
    
    if not doc.xml_content:
        frappe.throw(_("No hay contenido XML para validar"))
    
    result = validate_ecf_signature(doc.xml_content)
    
    # Actualizar documento
    doc.firma_valida = result.get('signature_verified', False)
    doc.certificado_valido = result.get('certificate_valid', False)
    doc.fecha_validacion = frappe.utils.now()
    doc.validado_por = frappe.session.user
    doc.save()
    
    if result.get('valid'):
        frappe.msgprint(
            _("Firma digital válida"),
            indicator="green"
        )
    else:
        frappe.msgprint(
            _("Firma digital inválida: {0}").format(", ".join(result.get('errors', []))),
            indicator="orange"
        )
    
    return result
