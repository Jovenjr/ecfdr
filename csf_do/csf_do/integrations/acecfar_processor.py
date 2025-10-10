# -*- coding: utf-8 -*-
"""
Procesador de e-CF Recibidos (ACECFAR)
Crea automáticamente Purchase Invoice desde e-CF de proveedores
"""

import frappe
from frappe import _
from typing import Dict, List, Optional, Any
from csf_do.csf_do.utils.acecfar_parser import parse_ecf_xml
from csf_do.csf_do.utils.signature_validator import validate_ecf_signature


class ACECFARProcessor:
    """
    Procesador de e-CF recibidos.
    Convierte e-CF de proveedores en Purchase Invoice de ERPNext.
    """
    
    def __init__(self):
        self.company = self._get_default_company()
    
    def process_ecf(self, xml_content: str, validate_signature: bool = True) -> Dict[str, Any]:
        """
        Procesa un e-CF recibido completo
        
        Args:
            xml_content: Contenido XML del e-CF
            validate_signature: Si validar firma digital
            
        Returns:
            Resultado del procesamiento
        """
        result = {
            'success': False,
            'purchase_invoice': None,
            'ecf_recibido': None,
            'errors': [],
            'warnings': []
        }
        
        try:
            # 1. Parsear XML
            frappe.publish_realtime('acecfar_progress', {'step': 'parsing', 'message': 'Parseando XML...'})
            parsed_data = parse_ecf_xml(xml_content)
            
            # 2. Validar firma digital (opcional)
            if validate_signature:
                frappe.publish_realtime('acecfar_progress', {'step': 'validating', 'message': 'Validando firma digital...'})
                sig_result = validate_ecf_signature(xml_content)
                
                if not sig_result.get('valid'):
                    result['warnings'].append("Firma digital no válida: " + ", ".join(sig_result.get('errors', [])))
                    # No bloqueamos, solo advertimos
            
            # 3. Crear registro de e-CF Recibido
            frappe.publish_realtime('acecfar_progress', {'step': 'creating_record', 'message': 'Creando registro...'})
            ecf_recibido = self._create_ecf_recibido_record(parsed_data, xml_content)
            result['ecf_recibido'] = ecf_recibido.name
            
            # 4. Verificar si ya existe Purchase Invoice para este e-CF
            existing_pi = self._check_existing_purchase_invoice(parsed_data['header']['encf'])
            if existing_pi:
                result['warnings'].append(f"Ya existe Purchase Invoice {existing_pi} para este e-CF")
                ecf_recibido.purchase_invoice = existing_pi
                ecf_recibido.status = "Duplicado"
                ecf_recibido.save()
                result['purchase_invoice'] = existing_pi
                result['success'] = True
                return result
            
            # 5. Obtener o crear Supplier
            frappe.publish_realtime('acecfar_progress', {'step': 'supplier', 'message': 'Verificando proveedor...'})
            supplier = self._get_or_create_supplier(parsed_data['emisor'])
            
            # 6. Crear Purchase Invoice
            frappe.publish_realtime('acecfar_progress', {'step': 'invoice', 'message': 'Creando factura de compra...'})
            pi = self._create_purchase_invoice(parsed_data, supplier)
            
            # 7. Actualizar e-CF Recibido
            ecf_recibido.purchase_invoice = pi.name
            ecf_recibido.status = "Procesado"
            ecf_recibido.save()
            
            result['success'] = True
            result['purchase_invoice'] = pi.name
            
            frappe.publish_realtime('acecfar_progress', {'step': 'complete', 'message': 'Procesamiento completado'})
            
        except Exception as e:
            result['errors'].append(str(e))
            frappe.log_error(f"Error procesando e-CF: {str(e)}", "ACECFAR Processor")
        
        return result
    
    def _create_ecf_recibido_record(self, parsed_data: Dict, xml_content: str) -> Any:
        """Crea el registro de e-CF Recibido"""
        doc = frappe.get_doc({
            'doctype': 'e-CF Recibido',
            'encf': parsed_data['header']['encf'],
            'tipo_ecf': parsed_data['header']['tipo_ecf'],
            'fecha_emision': parsed_data['header']['fecha_emision'],
            'rnc_emisor': parsed_data['emisor']['rnc'],
            'razon_social_emisor': parsed_data['emisor']['razon_social'],
            'monto_total': parsed_data['totales']['monto_total'],
            'total_itbis': parsed_data['totales'].get('total_itbis', 0),
            'xml_content': xml_content,
            'status': 'Pendiente',
            'company': self.company
        })
        doc.insert()
        return doc
    
    def _check_existing_purchase_invoice(self, encf: str) -> Optional[str]:
        """Verifica si ya existe Purchase Invoice para este e-CF"""
        existing = frappe.db.get_value(
            'Purchase Invoice',
            {'ncf': encf, 'docstatus': ['!=', 2]},
            'name'
        )
        return existing
    
    def _get_or_create_supplier(self, emisor_data: Dict) -> str:
        """Obtiene o crea el Supplier"""
        rnc = emisor_data.get('rnc')
        
        if not rnc:
            frappe.throw("RNC del emisor no encontrado")
        
        # Buscar supplier existente por RNC
        existing = frappe.db.get_value(
            'Supplier',
            {'tax_id': rnc},
            'name'
        )
        
        if existing:
            return existing
        
        # Crear nuevo supplier
        razon_social = emisor_data.get('razon_social', f'Proveedor {rnc}')
        
        supplier = frappe.get_doc({
            'doctype': 'Supplier',
            'supplier_name': razon_social,
            'supplier_group': self._get_default_supplier_group(),
            'tax_id': rnc,
            'supplier_type': 'Company',
            'country': 'Dominican Republic'
        })
        
        # Agregar dirección si existe
        if emisor_data.get('direccion'):
            supplier.append('address', {
                'address_line1': emisor_data.get('direccion'),
                'city': emisor_data.get('municipio', ''),
                'state': emisor_data.get('provincia', ''),
                'country': 'Dominican Republic'
            })
        
        # Agregar contacto si existe
        if emisor_data.get('correo') or emisor_data.get('telefono'):
            supplier.append('contact', {
                'email_id': emisor_data.get('correo'),
                'phone': emisor_data.get('telefono')
            })
        
        supplier.insert()
        
        frappe.msgprint(f"Proveedor {razon_social} creado automáticamente", indicator="blue")
        
        return supplier.name
    
    def _create_purchase_invoice(self, parsed_data: Dict, supplier: str) -> Any:
        """Crea la Purchase Invoice"""
        header = parsed_data['header']
        totales = parsed_data['totales']
        items = parsed_data['items']
        
        # Crear Purchase Invoice
        pi = frappe.get_doc({
            'doctype': 'Purchase Invoice',
            'supplier': supplier,
            'company': self.company,
            'posting_date': header.get('fecha_emision'),
            'due_date': header.get('fecha_vencimiento') or header.get('fecha_emision'),
            'ncf': header.get('encf'),
            'ncf_type': self._map_ecf_type_to_ncf_type(header.get('tipo_ecf')),
            'currency': 'DOP',  # TODO: Detectar moneda del XML
            'is_return': header.get('indicador_nota_credito') == '1',
            'bill_no': header.get('encf'),
            'bill_date': header.get('fecha_emision')
        })
        
        # Agregar ítems
        for item_data in items:
            pi.append('items', self._map_item(item_data))
        
        # Agregar impuestos
        tax_template = self._get_or_create_tax_template(totales)
        if tax_template:
            pi.taxes_and_charges = tax_template
        
        # Calcular totales
        pi.run_method('calculate_taxes_and_totals')
        
        # Validar que los totales coincidan
        self._validate_totals(pi, totales)
        
        # Guardar
        pi.insert()
        
        frappe.msgprint(f"Purchase Invoice {pi.name} creada exitosamente", indicator="green")
        
        return pi
    
    def _map_item(self, item_data: Dict) -> Dict:
        """Mapea un ítem del e-CF a un ítem de Purchase Invoice"""
        # Buscar item por código
        item_code = self._find_or_create_item(item_data)
        
        return {
            'item_code': item_code,
            'item_name': item_data.get('descripcion_item') or item_data.get('nombre_item'),
            'description': item_data.get('descripcion_item'),
            'qty': item_data.get('cantidad_item', 1),
            'uom': self._map_uom(item_data.get('unidad_medida')),
            'rate': item_data.get('precio_unitario', 0),
            'amount': item_data.get('monto_item', 0),
            'discount_amount': item_data.get('descuento', 0)
        }
    
    def _find_or_create_item(self, item_data: Dict) -> str:
        """Encuentra o crea un Item"""
        codigo = item_data.get('codigo_producto')
        
        # Si tiene código, buscar
        if codigo:
            existing = frappe.db.get_value('Item', {'item_code': codigo}, 'name')
            if existing:
                return existing
        
        # Crear item genérico
        item_name = item_data.get('nombre_item') or item_data.get('descripcion_item') or 'Item Genérico'
        
        # Verificar si ya existe por nombre
        existing = frappe.db.get_value('Item', {'item_name': item_name}, 'name')
        if existing:
            return existing
        
        # Crear nuevo item
        item = frappe.get_doc({
            'doctype': 'Item',
            'item_code': codigo or frappe.generate_hash(length=10),
            'item_name': item_name,
            'item_group': self._get_default_item_group(),
            'stock_uom': self._map_uom(item_data.get('unidad_medida')),
            'is_stock_item': 0,
            'is_purchase_item': 1
        })
        item.insert()
        
        return item.name
    
    def _map_uom(self, uom: Optional[str]) -> str:
        """Mapea unidad de medida"""
        if not uom:
            return 'Nos'
        
        uom_map = {
            'UND': 'Nos',
            'UNIDAD': 'Nos',
            'KG': 'Kg',
            'KILOGRAMO': 'Kg',
            'LT': 'Litre',
            'LITRO': 'Litre',
            'MT': 'Meter',
            'METRO': 'Meter',
            'CJ': 'Box',
            'CAJA': 'Box'
        }
        
        return uom_map.get(uom.upper(), 'Nos')
    
    def _map_ecf_type_to_ncf_type(self, ecf_type: str) -> str:
        """Mapea tipo de e-CF a tipo de NCF"""
        type_map = {
            '31': 'Crédito Fiscal',
            '32': 'Consumo',
            '33': 'Nota de Débito',
            '34': 'Nota de Crédito',
            '41': 'Compras',
            '43': 'Gastos Menores',
            '44': 'Regímenes Especiales',
            '45': 'Gubernamental',
            '46': 'Exportaciones',
            '47': 'Pagos al Exterior'
        }
        return type_map.get(ecf_type, 'Crédito Fiscal')
    
    def _get_or_create_tax_template(self, totales: Dict) -> Optional[str]:
        """Obtiene o crea template de impuestos"""
        # Por ahora retornar None, el cálculo se hace manual
        # TODO: Crear templates dinámicos según tasas de ITBIS
        return None
    
    def _validate_totals(self, pi: Any, totales: Dict):
        """Valida que los totales de PI coincidan con e-CF"""
        expected_total = totales.get('monto_total', 0)
        actual_total = pi.grand_total
        
        # Permitir diferencia de 1 peso por redondeo
        if abs(expected_total - actual_total) > 1:
            frappe.msgprint(
                f"Advertencia: Total de PI ({actual_total}) difiere del e-CF ({expected_total})",
                indicator="orange"
            )
    
    def _get_default_company(self) -> str:
        """Obtiene la compañía por defecto"""
        return frappe.defaults.get_user_default('Company') or frappe.db.get_single_value('Global Defaults', 'default_company')
    
    def _get_default_supplier_group(self) -> str:
        """Obtiene el grupo de proveedores por defecto"""
        return frappe.db.get_single_value('Buying Settings', 'supplier_group') or 'All Supplier Groups'
    
    def _get_default_item_group(self) -> str:
        """Obtiene el grupo de items por defecto"""
        return frappe.db.get_single_value('Stock Settings', 'item_group') or 'All Item Groups'


# ==================== API PÚBLICA ====================

@frappe.whitelist()
def process_ecf_from_xml(xml_content: str, validate_signature: bool = True) -> Dict:
    """
    API pública para procesar e-CF desde XML
    
    Args:
        xml_content: Contenido XML del e-CF
        validate_signature: Si validar firma digital
        
    Returns:
        Resultado del procesamiento
    """
    processor = ACECFARProcessor()
    return processor.process_ecf(xml_content, validate_signature)


@frappe.whitelist()
def process_ecf_from_file(file_url: str, validate_signature: bool = True) -> Dict:
    """
    API pública para procesar e-CF desde archivo
    
    Args:
        file_url: URL del archivo XML
        validate_signature: Si validar firma digital
        
    Returns:
        Resultado del procesamiento
    """
    # Leer archivo
    file_doc = frappe.get_doc('File', {'file_url': file_url})
    xml_content = file_doc.get_content()
    
    processor = ACECFARProcessor()
    return processor.process_ecf(xml_content.decode('utf-8'), validate_signature)


@frappe.whitelist()
def reprocess_ecf_recibido(ecf_recibido_name: str) -> Dict:
    """
    Reprocesa un e-CF Recibido existente
    
    Args:
        ecf_recibido_name: Nombre del documento e-CF Recibido
        
    Returns:
        Resultado del procesamiento
    """
    doc = frappe.get_doc('e-CF Recibido', ecf_recibido_name)
    
    processor = ACECFARProcessor()
    return processor.process_ecf(doc.xml_content, validate_signature=False)
