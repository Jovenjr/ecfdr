# Copyright (c) 2025, Navari Ltd and contributors
# For license information, please see license.txt

def get_report_config():
    """Configuración de reportes específicos de República Dominicana"""
    return {
        "default_filters": {
            "country": "Dominican Republic",
            "currency": "DOP"
        },
        "date_format": "dd-mm-yyyy",
        "number_format": "#,###.##"
    }

def get_dominican_reports():
    """Lista de reportes específicos de RD"""
    return [
        "Dominican RST Declaration Report",
        "Dominican RST Monthly Report", 
        "Dominican Sales Tax Report",
        "Dominican Purchase Tax Report",
        "Dominican Payroll Register Report",
        "Dominican Bank Payroll Advice Report",
        "Dominican SFS Report",
        "Dominican SNS Report",
        "Dominican Educational Loans Report",
        "Dominican IPI Contribution Report"
    ]
