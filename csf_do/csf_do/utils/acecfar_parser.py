# -*- coding: utf-8 -*-
"""
Parser de e-CF Recibidos (ACECFAR)
Parsea XML de e-CF recibidos de proveedores
"""

import frappe
from lxml import etree
from typing import Dict, List, Optional, Any
from datetime import datetime


class ACECFARParser:
    """
    Parser de e-CF recibidos de proveedores.
    Extrae toda la información necesaria para crear Purchase Invoice.
    """
    
    def __init__(self):
        self.namespaces = {
            'ecf': 'http://dgii.gov.do/ecf/v1.0',
            'ds': 'http://www.w3.org/2000/09/xmldsig#'
        }
    
    def parse_xml(self, xml_content: str) -> Dict[str, Any]:
        """
        Parsea un XML de e-CF completo
        
        Args:
            xml_content: Contenido XML del e-CF
            
        Returns:
            Diccionario con todos los datos parseados
        """
        try:
            # Parsear XML
            tree = etree.fromstring(xml_content.encode('utf-8'))
            
            # Extraer todas las secciones
            result = {
                'xml_original': xml_content,
                'header': self.extract_header(tree),
                'emisor': self.extract_emisor(tree),
                'comprador': self.extract_comprador(tree),
                'items': self.extract_items(tree),
                'totales': self.extract_totales(tree),
                'informaciones_adicionales': self.extract_info_adicional(tree),
                'signature': self.extract_signature(tree),
                'parsed_at': datetime.now().isoformat()
            }
            
            # Validaciones básicas
            self._validate_parsed_data(result)
            
            return result
            
        except etree.XMLSyntaxError as e:
            frappe.throw(f"Error de sintaxis XML: {str(e)}")
        except Exception as e:
            frappe.log_error(f"Error parseando e-CF: {str(e)}", "ACECFAR Parser Error")
            frappe.throw(f"Error parseando e-CF: {str(e)}")
    
    def extract_header(self, tree) -> Dict[str, Any]:
        """Extrae información del encabezado"""
        header = {}
        
        try:
            encabezado = tree.find('.//ecf:Encabezado', self.namespaces)
            if encabezado is None:
                encabezado = tree.find('.//Encabezado')
            
            if encabezado is not None:
                # Versión
                version = encabezado.find('.//ecf:Version', self.namespaces)
                if version is None:
                    version = encabezado.find('.//Version')
                header['version'] = version.text if version is not None else '1.0'
                
                # IdDoc
                id_doc = encabezado.find('.//ecf:IdDoc', self.namespaces)
                if id_doc is None:
                    id_doc = encabezado.find('.//IdDoc')
                
                if id_doc is not None:
                    header['tipo_ecf'] = self._get_text(id_doc, 'TipoeCF')
                    header['encf'] = self._get_text(id_doc, 'eNCF')
                    header['fecha_emision'] = self._get_text(id_doc, 'FechaEmision')
                    header['fecha_vencimiento'] = self._get_text(id_doc, 'FechaVencimiento')
                    header['indicador_monto_gravado'] = self._get_text(id_doc, 'IndicadorMontoGravado')
                    header['indicador_envio_contigencia'] = self._get_text(id_doc, 'IndicadorEnvioContigencia')
                    header['indicador_nota_credito'] = self._get_text(id_doc, 'IndicadorNotaCredito')
                    header['tipo_ingreso'] = self._get_text(id_doc, 'TipoIngreso')
                    header['tipo_pago'] = self._get_text(id_doc, 'TipoPago')
                    header['forma_pago'] = self._get_text(id_doc, 'FormaPago')
                    header['fecha_pago'] = self._get_text(id_doc, 'FechaPago')
                    header['monto_pago'] = self._get_float(id_doc, 'MontoPago')
                    header['numero_orden_compra'] = self._get_text(id_doc, 'NumeroOrdenCompra')
                
                # Tablas de Referencia
                tablas = encabezado.find('.//ecf:TablasDeReferencia', self.namespaces)
                if tablas is None:
                    tablas = encabezado.find('.//TablasDeReferencia')
                
                if tablas is not None:
                    header['tabla_codigo_producto'] = self._get_text(tablas, 'TablaCodigoProducto')
                    header['tabla_unidad_medida'] = self._get_text(tablas, 'TablaUnidadMedida')
                    header['tabla_forma_pago'] = self._get_text(tablas, 'TablaFormaPago')
        
        except Exception as e:
            frappe.log_error(f"Error extrayendo header: {str(e)}", "ACECFAR Parser")
        
        return header
    
    def extract_emisor(self, tree) -> Dict[str, Any]:
        """Extrae información del emisor (proveedor)"""
        emisor = {}
        
        try:
            emisor_node = tree.find('.//ecf:Emisor', self.namespaces)
            if emisor_node is None:
                emisor_node = tree.find('.//Emisor')
            
            if emisor_node is not None:
                emisor['rnc'] = self._get_text(emisor_node, 'RNCEmisor')
                emisor['razon_social'] = self._get_text(emisor_node, 'RazonSocialEmisor')
                emisor['nombre_comercial'] = self._get_text(emisor_node, 'NombreComercial')
                emisor['sucursal'] = self._get_text(emisor_node, 'Sucursal')
                emisor['direccion'] = self._get_text(emisor_node, 'DireccionEmisor')
                emisor['municipio'] = self._get_text(emisor_node, 'Municipio')
                emisor['provincia'] = self._get_text(emisor_node, 'Provincia')
                emisor['telefono'] = self._get_text(emisor_node, 'TelefonoEmisor')
                emisor['fax'] = self._get_text(emisor_node, 'FaxEmisor')
                emisor['correo'] = self._get_text(emisor_node, 'CorreoEmisor')
                emisor['website'] = self._get_text(emisor_node, 'WebSite')
                emisor['actividad_economica'] = self._get_text(emisor_node, 'ActividadEconomica')
                emisor['codigo_vendedor'] = self._get_text(emisor_node, 'CodigoVendedor')
                emisor['zona'] = self._get_text(emisor_node, 'Zona')
                emisor['ruta'] = self._get_text(emisor_node, 'Ruta')
                emisor['fecha_emision'] = self._get_text(emisor_node, 'FechaEmision')
        
        except Exception as e:
            frappe.log_error(f"Error extrayendo emisor: {str(e)}", "ACECFAR Parser")
        
        return emisor
    
    def extract_comprador(self, tree) -> Dict[str, Any]:
        """Extrae información del comprador (nuestra empresa)"""
        comprador = {}
        
        try:
            comprador_node = tree.find('.//ecf:Comprador', self.namespaces)
            if comprador_node is None:
                comprador_node = tree.find('.//Comprador')
            
            if comprador_node is not None:
                comprador['rnc'] = self._get_text(comprador_node, 'RNCComprador')
                comprador['razon_social'] = self._get_text(comprador_node, 'RazonSocialComprador')
                comprador['contacto'] = self._get_text(comprador_node, 'ContactoComprador')
                comprador['correo'] = self._get_text(comprador_node, 'CorreoComprador')
                comprador['direccion'] = self._get_text(comprador_node, 'DireccionComprador')
                comprador['municipio'] = self._get_text(comprador_node, 'MunicipioComprador')
                comprador['provincia'] = self._get_text(comprador_node, 'ProvinciaComprador')
                comprador['pais'] = self._get_text(comprador_node, 'PaisComprador')
                comprador['telefono'] = self._get_text(comprador_node, 'TelefonoComprador')
        
        except Exception as e:
            frappe.log_error(f"Error extrayendo comprador: {str(e)}", "ACECFAR Parser")
        
        return comprador
    
    def extract_items(self, tree) -> List[Dict[str, Any]]:
        """Extrae los ítems del e-CF"""
        items = []
        
        try:
            detalles = tree.find('.//ecf:DetallesItems', self.namespaces)
            if detalles is None:
                detalles = tree.find('.//DetallesItems')
            
            if detalles is not None:
                item_nodes = detalles.findall('.//ecf:Item', self.namespaces)
                if not item_nodes:
                    item_nodes = detalles.findall('.//Item')
                
                for item_node in item_nodes:
                    item = {
                        'numero_linea': self._get_int(item_node, 'NumeroLinea'),
                        'indicador_facturacion': self._get_text(item_node, 'IndicadorFacturacion'),
                        'nombre_item': self._get_text(item_node, 'NombreItem'),
                        'descripcion_item': self._get_text(item_node, 'DescripcionItem'),
                        'cantidad_item': self._get_float(item_node, 'CantidadItem'),
                        'unidad_medida': self._get_text(item_node, 'UnidadMedida'),
                        'precio_unitario': self._get_float(item_node, 'PrecioUnitarioItem'),
                        'descuento': self._get_float(item_node, 'DescuentoItem'),
                        'recargo': self._get_float(item_node, 'RecargoItem'),
                        'monto_item': self._get_float(item_node, 'MontoItem'),
                        'codigo_producto': self._get_text(item_node, 'CodigoProducto'),
                        'codigo_producto_comprador': self._get_text(item_node, 'CodigoProductoComprador'),
                        'fecha_fabricacion': self._get_text(item_node, 'FechaFabricacion'),
                        'fecha_vencimiento': self._get_text(item_node, 'FechaVencimiento'),
                        'numero_serie': self._get_text(item_node, 'NumeroSerie'),
                        'numero_lote': self._get_text(item_node, 'NumeroLote'),
                        'numero_placa': self._get_text(item_node, 'NumeroPlaca'),
                        'numero_referencia': self._get_text(item_node, 'NumeroReferencia'),
                        'numero_pedido': self._get_text(item_node, 'NumeroPedido'),
                        'numero_orden_compra': self._get_text(item_node, 'NumeroOrdenCompra'),
                        'numero_contrato': self._get_text(item_node, 'NumeroContrato'),
                        'numero_guia': self._get_text(item_node, 'NumeroGuia'),
                        'numero_factura_origen': self._get_text(item_node, 'NumeroFacturaOrigen'),
                        'fecha_factura_origen': self._get_text(item_node, 'FechaFacturaOrigen'),
                        'numero_linea_factura_origen': self._get_int(item_node, 'NumeroLineaFacturaOrigen'),
                    }
                    items.append(item)
        
        except Exception as e:
            frappe.log_error(f"Error extrayendo items: {str(e)}", "ACECFAR Parser")
        
        return items
    
    def extract_totales(self, tree) -> Dict[str, Any]:
        """Extrae los totales del e-CF"""
        totales = {}
        
        try:
            totales_node = tree.find('.//ecf:Totales', self.namespaces)
            if totales_node is None:
                totales_node = tree.find('.//Totales')
            
            if totales_node is not None:
                totales['monto_gravado_total'] = self._get_float(totales_node, 'MontoGravadoTotal')
                totales['monto_gravado_i1'] = self._get_float(totales_node, 'MontoGravadoI1')
                totales['monto_gravado_i2'] = self._get_float(totales_node, 'MontoGravadoI2')
                totales['monto_gravado_i3'] = self._get_float(totales_node, 'MontoGravadoI3')
                totales['monto_exento'] = self._get_float(totales_node, 'MontoExento')
                totales['itbis_1'] = self._get_float(totales_node, 'ITBIS1')
                totales['itbis_2'] = self._get_float(totales_node, 'ITBIS2')
                totales['itbis_3'] = self._get_float(totales_node, 'ITBIS3')
                totales['total_itbis'] = self._get_float(totales_node, 'TotalITBIS')
                totales['monto_impuesto_adicional'] = self._get_float(totales_node, 'MontoImpuestoAdicional')
                totales['impuesto_adicional_1'] = self._get_float(totales_node, 'ImpuestoAdicional1')
                totales['impuesto_adicional_2'] = self._get_float(totales_node, 'ImpuestoAdicional2')
                totales['impuesto_adicional_3'] = self._get_float(totales_node, 'ImpuestoAdicional3')
                totales['monto_propina_legal'] = self._get_float(totales_node, 'MontoPropinaLegal')
                totales['monto_total'] = self._get_float(totales_node, 'MontoTotal')
                totales['monto_no_facturable'] = self._get_float(totales_node, 'MontoNoFacturable')
                totales['monto_periodo'] = self._get_float(totales_node, 'MontoPeriodo')
                totales['saldo_anterior'] = self._get_float(totales_node, 'SaldoAnterior')
                totales['monto_avance'] = self._get_float(totales_node, 'MontoAvance')
                totales['valor_pagar'] = self._get_float(totales_node, 'ValorPagar')
                totales['total_itbis_retenido'] = self._get_float(totales_node, 'TotalITBISRetenido')
                totales['total_isr_retenido'] = self._get_float(totales_node, 'TotalISRRetenido')
                totales['total_isr_percepcion'] = self._get_float(totales_node, 'TotalISRPercepcion')
                totales['total_impuesto_selectivo_consumo'] = self._get_float(totales_node, 'TotalImpuestoSelectivoConsumo')
                totales['total_otros_impuestos'] = self._get_float(totales_node, 'TotalOtrosImpuestos')
        
        except Exception as e:
            frappe.log_error(f"Error extrayendo totales: {str(e)}", "ACECFAR Parser")
        
        return totales
    
    def extract_info_adicional(self, tree) -> Dict[str, Any]:
        """Extrae información adicional"""
        info = {}
        
        try:
            info_node = tree.find('.//ecf:InformacionesAdicionales', self.namespaces)
            if info_node is None:
                info_node = tree.find('.//InformacionesAdicionales')
            
            if info_node is not None:
                info['fecha_hora_certificacion'] = self._get_text(info_node, 'FechaHoraCertificacion')
                info['codigo_seguridad'] = self._get_text(info_node, 'CodigoSeguridad')
                info['numero_autorizacion'] = self._get_text(info_node, 'NumeroAutorizacion')
                info['informacion_adicional'] = self._get_text(info_node, 'InformacionAdicional')
        
        except Exception as e:
            frappe.log_error(f"Error extrayendo info adicional: {str(e)}", "ACECFAR Parser")
        
        return info
    
    def extract_signature(self, tree) -> Dict[str, Any]:
        """Extrae información de la firma digital"""
        signature = {}
        
        try:
            sig_node = tree.find('.//ds:Signature', self.namespaces)
            if sig_node is None:
                sig_node = tree.find('.//Signature')
            
            if sig_node is not None:
                signature['present'] = True
                
                # SignatureValue
                sig_value = sig_node.find('.//ds:SignatureValue', self.namespaces)
                if sig_value is None:
                    sig_value = sig_node.find('.//SignatureValue')
                signature['signature_value'] = sig_value.text if sig_value is not None else None
                
                # KeyInfo
                key_info = sig_node.find('.//ds:KeyInfo', self.namespaces)
                if key_info is None:
                    key_info = sig_node.find('.//KeyInfo')
                
                if key_info is not None:
                    x509_cert = key_info.find('.//ds:X509Certificate', self.namespaces)
                    if x509_cert is None:
                        x509_cert = key_info.find('.//X509Certificate')
                    signature['certificate'] = x509_cert.text if x509_cert is not None else None
            else:
                signature['present'] = False
        
        except Exception as e:
            frappe.log_error(f"Error extrayendo firma: {str(e)}", "ACECFAR Parser")
            signature['present'] = False
        
        return signature
    
    # ==================== UTILIDADES ====================
    
    def _get_text(self, parent, tag: str) -> Optional[str]:
        """Obtiene texto de un elemento"""
        try:
            # Intentar con namespace
            elem = parent.find(f'.//ecf:{tag}', self.namespaces)
            if elem is None:
                # Intentar sin namespace
                elem = parent.find(f'.//{tag}')
            
            return elem.text.strip() if elem is not None and elem.text else None
        except:
            return None
    
    def _get_float(self, parent, tag: str) -> float:
        """Obtiene valor float de un elemento"""
        text = self._get_text(parent, tag)
        try:
            return float(text) if text else 0.0
        except:
            return 0.0
    
    def _get_int(self, parent, tag: str) -> int:
        """Obtiene valor int de un elemento"""
        text = self._get_text(parent, tag)
        try:
            return int(text) if text else 0
        except:
            return 0
    
    def _validate_parsed_data(self, data: Dict):
        """Valida que los datos parseados sean correctos"""
        # Validar campos obligatorios
        if not data.get('header', {}).get('encf'):
            frappe.throw("e-CF no contiene número de comprobante (eNCF)")
        
        if not data.get('emisor', {}).get('rnc'):
            frappe.throw("e-CF no contiene RNC del emisor")
        
        if not data.get('totales', {}).get('monto_total'):
            frappe.throw("e-CF no contiene monto total")
        
        if not data.get('items'):
            frappe.throw("e-CF no contiene ítems")


# ==================== API PÚBLICA ====================

def parse_ecf_xml(xml_content: str) -> Dict[str, Any]:
    """
    Función pública para parsear un e-CF
    
    Args:
        xml_content: Contenido XML del e-CF
        
    Returns:
        Diccionario con todos los datos parseados
    """
    parser = ACECFARParser()
    return parser.parse_xml(xml_content)


def validate_ecf_structure(xml_content: str) -> bool:
    """
    Valida que un XML tenga la estructura correcta de e-CF
    
    Args:
        xml_content: Contenido XML
        
    Returns:
        True si es válido, False si no
    """
    try:
        parser = ACECFARParser()
        data = parser.parse_xml(xml_content)
        return True
    except:
        return False
