# Copyright (c) 2025, Navari Ltd and contributors
# For license information, please see license.txt

import pytest
import unittest
import frappe
from frappe.tests.utils import FrappeTestCase

@pytest.mark.requires_bench
class TestCSFDOInstallation(FrappeTestCase):
    """Tests para validar la instalación de CSF DO"""
    
    def setUp(self):
        """Configuración inicial para tests"""
        pass
    
    def test_country_configured(self):
        """Test: Verificar que República Dominicana está configurada"""
        self.assertTrue(frappe.db.exists("Country", "Dominican Republic"))
    
    def test_currency_configured(self):
        """Test: Verificar que DOP está configurada"""
        self.assertTrue(frappe.db.exists("Currency", "DOP"))
    
    def test_roles_created(self):
        """Test: Verificar que los roles específicos están creados"""
        roles = ["Emisor e-CF", "Aprobador Comercial", "Administrador e-CF"]
        for role in roles:
            self.assertTrue(frappe.db.exists("Role", role))
    
    def test_warehouses_created(self):
        """Test: Verificar que los almacenes están creados"""
        self.assertTrue(frappe.db.exists("Warehouse", "Almacén Principal - RD"))
    
    def test_doctypes_exist(self):
        """Test: Verificar que los DocTypes específicos existen"""
        doctypes = [
            "e-CF",
            "DGII Configuration", 
            "Digital Certificate",
            "NCF HSCode"
        ]
        for doctype in doctypes:
            self.assertTrue(frappe.db.exists("DocType", doctype))
    
    def test_reports_exist(self):
        """Test: Verificar que los reportes específicos existen"""
        reports = [
            "Dominican RST Declaration Report",
            "Dominican Sales Tax Report",
            "Dominican Purchase Tax Report"
        ]
        for report in reports:
            self.assertTrue(frappe.db.exists("Report", report))
