# -*- coding: utf-8 -*-
# Copyright (c) 2025, AI Studio RD and contributors
# For license information, please see license.txt

"""
Utilidades de validación para DGII República Dominicana
"""

from __future__ import unicode_literals
import frappe
import re


def validate_rnc(rnc):
    """
    Valida un RNC (Registro Nacional del Contribuyente) dominicano
    
    Formato válido:
    - RNC Persona Jurídica: 9 dígitos
    - RNC Persona Física: 11 dígitos (igual a cédula)
    
    Args:
        rnc: String con el RNC a validar
        
    Returns:
        dict: {"valid": bool, "message": str, "tipo": str}
    """
    
    if not rnc:
        return {
            "valid": False,
            "message": "RNC no puede estar vacío",
            "tipo": None
        }
    
    # Limpiar RNC (remover guiones y espacios)
    rnc_limpio = re.sub(r'[-\s]', '', str(rnc))
    
    # Validar que solo contenga dígitos
    if not rnc_limpio.isdigit():
        return {
            "valid": False,
            "message": "RNC debe contener solo números",
            "tipo": None
        }
    
    # Determinar tipo según longitud
    longitud = len(rnc_limpio)
    
    if longitud == 9:
        # RNC Persona Jurídica
        if _validate_rnc_juridica(rnc_limpio):
            return {
                "valid": True,
                "message": "RNC de Persona Jurídica válido",
                "tipo": "Persona Jurídica"
            }
        else:
            return {
                "valid": False,
                "message": "RNC de Persona Jurídica inválido (dígito verificador incorrecto)",
                "tipo": "Persona Jurídica"
            }
            
    elif longitud == 11:
        # RNC Persona Física (Cédula)
        if _validate_cedula(rnc_limpio):
            return {
                "valid": True,
                "message": "RNC/Cédula válido",
                "tipo": "Persona Física"
            }
        else:
            return {
                "valid": False,
                "message": "RNC/Cédula inválido (dígito verificador incorrecto)",
                "tipo": "Persona Física"
            }
    else:
        return {
            "valid": False,
            "message": f"Longitud inválida: debe ser 9 (Persona Jurídica) u 11 (Persona Física) dígitos",
            "tipo": None
        }


def _validate_rnc_juridica(rnc):
    """
    Valida RNC de Persona Jurídica (9 dígitos) usando algoritmo de módulo 11
    
    Args:
        rnc: String de 9 dígitos
        
    Returns:
        bool: True si es válido
    """
    if len(rnc) != 9:
        return False
        
    # Extraer dígito verificador
    digitos = [int(d) for d in rnc[:-1]]
    digito_verificador = int(rnc[-1])
    
    # Pesos para el algoritmo (de derecha a izquierda: 2,3,4,5,6,7,8,9)
    pesos = [9, 8, 7, 6, 5, 4, 3, 2]
    
    # Calcular suma ponderada
    suma = sum(d * p for d, p in zip(digitos, pesos))
    
    # Calcular módulo 11
    modulo = suma % 11
    
    # El dígito verificador es 11 - módulo, pero si es 11 se usa 0, si es 10 se usa 1
    digito_calculado = 11 - modulo
    if digito_calculado == 11:
        digito_calculado = 0
    elif digito_calculado == 10:
        digito_calculado = 1
        
    return digito_verificador == digito_calculado


def _validate_cedula(cedula):
    """
    Valida Cédula dominicana (11 dígitos) usando algoritmo de módulo 10
    
    Args:
        cedula: String de 11 dígitos
        
    Returns:
        bool: True si es válido
    """
    if len(cedula) != 11:
        return False
        
    # Extraer dígito verificador
    digitos = [int(d) for d in cedula[:-1]]
    digito_verificador = int(cedula[-1])
    
    # Aplicar algoritmo de Luhn modificado
    suma = 0
    for i, digito in enumerate(digitos):
        # Alternar multiplicación por 2 y 1
        if i % 2 == 0:
            producto = digito * 2
            # Si el producto es mayor a 9, sumar sus dígitos
            if producto > 9:
                producto = producto - 9
            suma += producto
        else:
            suma += digito
    
    # Calcular dígito verificador
    digito_calculado = (10 - (suma % 10)) % 10
    
    return digito_verificador == digito_calculado


def validate_itbis(amount, itbis_rate=18):
    """
    Valida que el ITBIS (Impuesto a la Transferencia de Bienes y Servicios) 
    esté calculado correctamente
    
    Args:
        amount: Monto base
        itbis_rate: Tasa de ITBIS (default 18%)
        
    Returns:
        dict: {"itbis": float, "total": float, "base": float}
    """
    base = float(amount)
    itbis = round(base * (itbis_rate / 100), 2)
    total = base + itbis
    
    return {
        "base": base,
        "itbis": itbis,
        "total": total,
        "rate": itbis_rate
    }


def validate_ncf_format(ncf):
    """
    Valida el formato de un NCF (Número de Comprobante Fiscal)
    
    Formato: BYYZZZZZZZZ
    - B: Serie (A o B)
    - YY: Tipo (01-17)
    - ZZZZZZZZ: Secuencia (8 dígitos)
    
    Args:
        ncf: String con el NCF
        
    Returns:
        dict: {"valid": bool, "message": str, "serie": str, "tipo": str, "secuencia": str}
    """
    if not ncf:
        return {
            "valid": False,
            "message": "NCF no puede estar vacío"
        }
    
    # Limpiar NCF
    ncf_limpio = ncf.strip().upper()
    
    # Validar longitud (11 caracteres)
    if len(ncf_limpio) != 11:
        return {
            "valid": False,
            "message": f"NCF debe tener 11 caracteres (tiene {len(ncf_limpio)})"
        }
    
    # Validar serie (primer carácter: A o B)
    serie = ncf_limpio[0]
    if serie not in ['A', 'B']:
        return {
            "valid": False,
            "message": f"Serie inválida '{serie}', debe ser A o B"
        }
    
    # Validar tipo (caracteres 2-3: 01-17)
    tipo = ncf_limpio[1:3]
    tipos_validos = [f"{i:02d}" for i in range(1, 18)]  # 01-17
    if tipo not in tipos_validos:
        return {
            "valid": False,
            "message": f"Tipo inválido '{tipo}', debe estar entre 01 y 17"
        }
    
    # Validar secuencia (caracteres 4-11: 8 dígitos)
    secuencia = ncf_limpio[3:]
    if not secuencia.isdigit() or len(secuencia) != 8:
        return {
            "valid": False,
            "message": f"Secuencia inválida '{secuencia}', debe ser 8 dígitos"
        }
    
    return {
        "valid": True,
        "message": "NCF válido",
        "serie": serie,
        "tipo": tipo,
        "secuencia": secuencia,
        "tipo_nombre": get_tipo_ncf_name(f"B{tipo}")
    }


def get_tipo_ncf_name(tipo_ncf):
    """
    Obtiene el nombre descriptivo de un tipo de NCF
    
    Args:
        tipo_ncf: Código del tipo (B01, B02, etc.)
        
    Returns:
        str: Nombre del tipo de NCF
    """
    tipos = {
        "B01": "Facturas de Crédito Fiscal",
        "B02": "Facturas de Consumo",
        "B03": "Notas de Débito",
        "B04": "Notas de Crédito",
        "B11": "Proveedores Informales",
        "B12": "Registro Único de Ingresos",
        "B13": "Gastos Menores",
        "B14": "Régimen Especial de Tributación",
        "B15": "Gubernamental",
        "B16": "Exportaciones",
        "B17": "Pagos al Exterior"
    }
    return tipos.get(tipo_ncf, "Tipo desconocido")


# ==================== API WHITELISTED METHODS ====================

@frappe.whitelist()
def check_rnc(rnc):
    """
    API para validar RNC desde el frontend
    
    Args:
        rnc: RNC a validar
        
    Returns:
        dict con resultado de validación
    """
    return validate_rnc(rnc)


@frappe.whitelist()
def check_ncf(ncf):
    """
    API para validar NCF desde el frontend
    
    Args:
        ncf: NCF a validar
        
    Returns:
        dict con resultado de validación
    """
    return validate_ncf_format(ncf)


@frappe.whitelist()
def calculate_itbis(amount, rate=18):
    """
    API para calcular ITBIS desde el frontend
    
    Args:
        amount: Monto base
        rate: Tasa de ITBIS (default 18)
        
    Returns:
        dict con cálculo de ITBIS
    """
    return validate_itbis(float(amount), float(rate))


@frappe.whitelist()
def validate_customer_rnc(customer):
    """
    Valida el RNC de un cliente
    
    Args:
        customer: Nombre del cliente
        
    Returns:
        dict con resultado de validación
    """
    customer_doc = frappe.get_doc("Customer", customer)
    
    if not customer_doc.tax_id:
        return {
            "valid": False,
            "message": "Cliente no tiene RNC/Cédula registrado"
        }
    
    return validate_rnc(customer_doc.tax_id)


# ==================== INVOICE VALIDATORS ====================

def validate_invoice_itbis(doc, method):
    """
    Hook para validar ITBIS en Sales Invoice y Purchase Invoice antes de submit
    
    Args:
        doc: Sales Invoice o Purchase Invoice document
        method: Método del hook (before_submit)
    """
    # Solo validar si tiene impuestos
    if not doc.taxes:
        return
    
    # Buscar el impuesto ITBIS (18%)
    itbis_tax = None
    for tax in doc.taxes:
        if tax.rate == 18 or "ITBIS" in tax.description.upper() or "IVA" in tax.description.upper():
            itbis_tax = tax
            break
    
    if not itbis_tax:
        return
    
    # Calcular ITBIS esperado
    expected_itbis = round(doc.net_total * 0.18, 2)
    actual_itbis = itbis_tax.tax_amount
    
    # Tolerancia de 0.02 por redondeo
    tolerance = 0.02
    difference = abs(expected_itbis - actual_itbis)
    
    if difference > tolerance:
        frappe.msgprint(
            f"""
            <b>Advertencia de validación ITBIS:</b><br>
            ITBIS calculado: {actual_itbis}<br>
            ITBIS esperado (18%): {expected_itbis}<br>
            Diferencia: {difference}
            """,
            indicator="orange",
            title="Validación ITBIS"
        )
    
    # Marcar como validado
    doc.custom_itbis_validado = 1
    doc.custom_itbis_rate = 18
    doc.custom_itbis_amount = actual_itbis

