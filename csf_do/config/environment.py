# Copyright (c) 2025, Navari Ltd and contributors
# For license information, please see license.txt

import os
import frappe

def get_environment_config():
    """Configuración específica por ambiente"""
    environment = os.getenv("FRAPPE_ENV", "development")
    
    configs = {
        "development": {
            "dgii_base_url": "https://precertificacion.dgii.gov.do",
            "debug_mode": True,
            "log_level": "DEBUG"
        },
        "staging": {
            "dgii_base_url": "https://certificacion.dgii.gov.do", 
            "debug_mode": False,
            "log_level": "INFO"
        },
        "production": {
            "dgii_base_url": "https://dgii.gov.do",
            "debug_mode": False,
            "log_level": "WARNING"
        }
    }
    
    return configs.get(environment, configs["development"])

def get_dgii_config():
    """Obtener configuración de DGII según ambiente"""
    env_config = get_environment_config()
    
    return {
        "base_url": env_config["dgii_base_url"],
        "timeout": 30,
        "retry_attempts": 3,
        "debug": env_config["debug_mode"]
    }
