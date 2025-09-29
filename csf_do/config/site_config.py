# Copyright (c) 2025, Navari Ltd and contributors
# For license information, please see license.txt

def get_site_config():
    """Configuración específica del sitio para República Dominicana"""
    return {
        "default_currency": "DOP",
        "country": "Dominican Republic",
        "timezone": "America/Santo_Domingo",
        "date_format": "dd-mm-yyyy",
        "time_format": "HH:mm:ss",
        "number_format": "#,###.##",
        "float_precision": 2,
        "currency_precision": 2
    }

def get_environment_config():
    """Configuración específica por ambiente"""
    return {
        "development": {
            "dgii_base_url": "https://precertificacion.dgii.gov.do",
            "debug_mode": True
        },
        "staging": {
            "dgii_base_url": "https://certificacion.dgii.gov.do",
            "debug_mode": False
        },
        "production": {
            "dgii_base_url": "https://dgii.gov.do",
            "debug_mode": False
        }
    }
