# Copyright (c) 2025, Navari Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe import _
import re

def validate_rnc(rnc):
    """Validar formato de RNC dominicano"""
    if not rnc:
        return False
    
    # Remover guiones y espacios
    rnc = re.sub(r'[-\s]', '', rnc)
    
    # Verificar que sea numérico y tenga 9 o 11 dígitos
    if not rnc.isdigit() or len(rnc) not in [9, 11]:
        return False
    
    return True

def validate_pin(pin):
    """Validar formato de PIN dominicano"""
    if not pin:
        return False
    
    # Remover guiones y espacios
    pin = re.sub(r'[-\s]', '', pin)
    
    # Verificar que sea alfanumérico y tenga 13 caracteres
    if not pin.isalnum() or len(pin) != 13:
        return False
    
    return True

def validate_phone(phone):
    """Validar formato de teléfono dominicano"""
    if not phone:
        return False
    
    # Remover espacios y guiones
    phone = re.sub(r'[\s-]', '', phone)
    
    # Verificar formato: +1-809-xxx-xxxx o 809-xxx-xxxx
    pattern = r'^(\+1-?)?809-\d{3}-\d{4}$'
    return bool(re.match(pattern, phone))

def validate_email(email):
    """Validar formato de email"""
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_ncf(ncf):
    """Validar formato de NCF"""
    if not ncf:
        return False
    
    # Verificar que sea alfanumérico y tenga 13 caracteres
    if not ncf.isalnum() or len(ncf) != 13:
        return False
    
    return True
