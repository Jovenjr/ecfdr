# Copyright (c) 2025, Navari Ltd and contributors
# For license information, please see license.txt

def get_system_config():
    """Configuración del sistema para República Dominicana"""
    return {
        "country": "Dominican Republic",
        "currency": "DOP",
        "timezone": "America/Santo_Domingo",
        "date_format": "dd-mm-yyyy",
        "time_format": "HH:mm:ss",
        "number_format": "#,###.##",
        "float_precision": 2,
        "currency_precision": 2,
        "fiscal_year_start": "01-01",
        "fiscal_year_end": "12-31"
    }

def get_tax_config():
    """Configuración de impuestos para República Dominicana"""
    return {
        "itbis_rate": 0.18,  # 18%
        "itbis_name": "ITBIS",
        "itbis_account": "ITBIS por Pagar",
        "itbis_receivable_account": "ITBIS por Cobrar"
    }

def get_payroll_config():
    """Configuración de nómina para República Dominicana"""
    return {
        "sfs_rate": 0.0287,  # 2.87%
        "sns_rate": 0.0301,  # 3.01%
        "rst_rate": 0.10,    # 10%
        "ipi_rate": 0.01     # 1%
    }
