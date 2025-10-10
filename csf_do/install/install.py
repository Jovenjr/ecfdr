# Copyright (c) 2025, Navari Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import now, today
import json
import os
from importlib import import_module


def before_install():
    """Configuraciones previas a la instalación"""
    frappe.logger().info("Iniciando instalación de CSF DO para República Dominicana...")
    
    # Validar versión de ERPNext
    validate_erpnext_version()
    
    # Validar dependencias
    validate_dependencies()


def after_install():
    """Configuraciones posteriores a la instalación"""
    frappe.logger().info("Configurando datos iniciales para República Dominicana...")
    
    try:
        # Configurar datos maestros básicos
        setup_dominican_data()
        
        # Configurar permisos específicos
        setup_dominican_permissions()
        
        # Configurar reportes
        setup_dominican_reports()
        
        # Validar configuración
        validate_installation()
        
        frappe.logger().info("Instalación de CSF DO completada exitosamente")
        
    except Exception as e:
        frappe.logger().error(f"Error durante la instalación: {str(e)}")
        raise


def before_migrate():
    """Migraciones previas"""
    frappe.logger().info("Ejecutando migraciones previas para CSF DO...")


def after_migrate():
    """Migraciones posteriores"""
    frappe.logger().info("Ejecutando migraciones posteriores para CSF DO...")
    
    # Insertar datos de NCF HSCode
    try:
        from csf_do.csf_do.doctype.ncf_hscode.ncf_hscode import insert_new_records
        insert_new_records()
    except Exception as e:
        frappe.logger().error(f"Error al insertar registros de NCF HSCode: {str(e)}")
        # No lanzar la excepción para no detener las migraciones

def _get_app_version(app_name: str) -> str | None:
    """Obtain the `__version__` attribute of an installed app."""
    try:
        module = import_module(app_name)
    except ModuleNotFoundError:
        return None

    return getattr(module, "__version__", None)


def validate_erpnext_version():
    """Validar que la versión de ERPNext sea compatible"""
    installed_apps = set(frappe.get_installed_apps())

    if "erpnext" not in installed_apps:
        frappe.throw(_("ERPNext no está instalado. CSF DO requiere ERPNext v13 o superior."))

    erpnext_version = _get_app_version("erpnext")

    if not erpnext_version:
        frappe.throw(_("No se pudo determinar la versión instalada de ERPNext."))
    
    # Verificar versión mínima (v13)
    major_version = int(erpnext_version.split('.')[0])
    if major_version < 13:
        frappe.throw(_("CSF DO requiere ERPNext v13 o superior. Versión actual: {0}").format(erpnext_version))


def validate_dependencies():
    """Validar dependencias requeridas"""
    required_apps = ["erpnext", "hrms"]

    installed_apps = set(frappe.get_installed_apps())

    for app in required_apps:
        if app not in installed_apps:
            frappe.throw(_("Aplicación requerida {0} no está instalada").format(app))


def setup_dominican_data():
    """Configurar datos iniciales específicos de República Dominicana"""
    
    # Configurar país por defecto
    setup_country()
    
    # Configurar moneda
    setup_currency()
    
    # Crear almacenes por defecto
    setup_default_warehouses()
    
    # Configurar cuentas contables dominicanas
    setup_dominican_accounts()
    
    # Configurar roles específicos
    setup_dominican_roles()


def setup_country():
    """Configurar República Dominicana como país por defecto"""
    if not frappe.db.exists("Country", "Dominican Republic"):
        country = frappe.get_doc({
            "doctype": "Country",
            "country_name": "Dominican Republic",
            "code": "DO",
            "date_format": "dd-mm-yyyy",
            "time_format": "HH:mm:ss",
            "timezone": "America/Santo_Domingo",
            "currency": "DOP"
        })
        country.insert(ignore_permissions=True)
        frappe.db.commit()


def setup_currency():
    """Configurar Peso Dominicano como moneda por defecto"""
    if not frappe.db.exists("Currency", "DOP"):
        currency = frappe.get_doc({
            "doctype": "Currency",
            "currency_name": "Peso Dominicano",
            "symbol": "RD$",
            "fraction": "Centavo",
            "fraction_units": 100,
            "smallest_currency_fraction_value": 0.01,
            "number_format": "#,###.##",
            "enabled": 1
        })
        currency.insert(ignore_permissions=True)
        frappe.db.commit()


def setup_default_warehouses():
    """Crear almacenes por defecto para República Dominicana"""
    default_company = frappe.defaults.get_user_default("Company")
    
    # Verificar si el campo warehouse_type existe
    has_warehouse_type = frappe.db.exists("DocField", {
        "parent": "Warehouse",
        "fieldname": "warehouse_type"
    })

    warehouses = [
        {
            "warehouse_name": "All Warehouses - RD",
            "is_group": 1,
            "parent_warehouse": "",
            "company": default_company
        },
        {
            "warehouse_name": "Almacén Principal - RD",
            "is_group": 0,
            "parent_warehouse": "All Warehouses - RD",
            "company": default_company
        }
    ]
    
    # Solo agregar warehouse_type si el campo existe y hay un tipo válido
    if has_warehouse_type:
        # Buscar un warehouse type existente
        warehouse_type = frappe.db.get_value("Warehouse Type", {"name": ["in", ["Store", "Almacén", "Default"]]})
        if warehouse_type:
            for wh in warehouses:
                wh["warehouse_type"] = warehouse_type
    
    for warehouse_data in warehouses:
        if not frappe.db.exists("Warehouse", warehouse_data["warehouse_name"]):
            try:
                warehouse = frappe.get_doc({
                    "doctype": "Warehouse",
                    **warehouse_data
                })
                warehouse.insert(ignore_permissions=True)
            except Exception as e:
                frappe.log_error(f"Error creating warehouse {warehouse_data.get('warehouse_name')}: {str(e)}")
                # Continuar con el siguiente almacén
                continue
    
    frappe.db.commit()


def setup_dominican_accounts():
    """Configurar cuentas contables específicas de República Dominicana"""
    # Esta función se puede expandir para crear un plan de cuentas dominicano
    # Por ahora, solo creamos las cuentas básicas de ITBIS
    itbis_accounts = [
        {
            "account_name": "ITBIS por Pagar",
            "account_type": "Tax",
            "parent_account": "Duties and Taxes",
            "is_group": 0
        },
        {
            "account_name": "ITBIS por Cobrar",
            "account_type": "Tax",
            "parent_account": "Duties and Taxes",
            "is_group": 0
        }
    ]
    
    for account_data in itbis_accounts:
        if not frappe.db.exists("Account", account_data["account_name"]):
            account = frappe.get_doc({
                "doctype": "Account",
                **account_data,
                "company": frappe.defaults.get_user_default("Company")
            })
            account.insert(ignore_permissions=True)
    
    frappe.db.commit()


def setup_dominican_roles():
    """Configurar roles específicos de República Dominicana"""
    roles = [
        {
            "role_name": "Emisor e-CF",
            "desk_access": 1,
            "is_custom": 1,
            "restrict_to_domain": None
        },
        {
            "role_name": "Aprobador Comercial",
            "desk_access": 1,
            "is_custom": 1,
            "restrict_to_domain": None
        },
        {
            "role_name": "Administrador e-CF",
            "desk_access": 1,
            "is_custom": 1,
            "restrict_to_domain": None
        }
    ]
    
    for role_data in roles:
        if not frappe.db.exists("Role", role_data["role_name"]):
            role = frappe.get_doc({
                "doctype": "Role",
                **role_data
            })
            role.insert(ignore_permissions=True)
    
    frappe.db.commit()


def setup_dominican_permissions():
    """Configurar permisos específicos para República Dominicana"""
    # Los permisos se configuran a través de fixtures
    # Esta función puede ser expandida para configuraciones adicionales
    pass


def setup_dominican_reports():
    """Configurar reportes específicos de República Dominicana"""
    # Los reportes se configuran automáticamente al instalar
    # Esta función puede ser expandida para configuraciones adicionales
    pass


def validate_installation():
    """Validar que la instalación se completó correctamente"""
    validation_checks = [
        ("Country", "Dominican Republic"),
        ("Currency", "DOP"),
        ("Role", "Emisor e-CF"),
        ("Role", "Aprobador Comercial"),
        ("Role", "Administrador e-CF")
    ]
    
    for doctype, name in validation_checks:
        if not frappe.db.exists(doctype, name):
            frappe.logger().warning(f"Validación fallida: {doctype} - {name} no encontrado")
    
    frappe.logger().info("Validación de instalación completada")


def get_installation_status():
    """Obtener estado de la instalación"""
    return {
        "country_configured": frappe.db.exists("Country", "Dominican Republic"),
        "currency_configured": frappe.db.exists("Currency", "DOP"),
        "roles_configured": all([
            frappe.db.exists("Role", "Emisor e-CF"),
            frappe.db.exists("Role", "Aprobador Comercial"),
            frappe.db.exists("Role", "Administrador e-CF")
        ]),
        "warehouses_configured": frappe.db.exists("Warehouse", "Almacén Principal - RD")
    }
