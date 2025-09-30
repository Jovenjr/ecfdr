import frappe
from frappe.tests.utils import FrappeTestCase

from csf_do.csf_do.report.dominican_republic_sales_tax_report.dominican_republic_sales_tax_report import (
    DominicanRepublicSalesTaxReport,
)
from csf_do.csf_do.report.dgii_607.dgii_607 import _parse_filters


class TestDominicanReports(FrappeTestCase):
    def setUp(self):
        super().setUp()
        self.company_name = "CSF DO Test Company"
        if not frappe.db.exists("Company", self.company_name):
            company = frappe.get_doc(
                {
                    "doctype": "Company",
                    "company_name": self.company_name,
                    "abbr": "CSDO",
                    "default_currency": "USD",
                    "country": "Dominican Republic",
                }
            )
            company.insert(ignore_permissions=True)
        frappe.defaults.set_user_default("Company", self.company_name)
        self.addCleanup(lambda: frappe.defaults.clear_user_default("Company"))

    def test_report_currency_uses_company_default_currency(self):
        report = DominicanRepublicSalesTaxReport({"company": self.company_name})
        self.assertEqual(report._get_report_currency(), "USD")

    def test_report_currency_defaults_to_dop_when_company_missing(self):
        frappe.defaults.clear_user_default("Company")
        report = DominicanRepublicSalesTaxReport({})
        self.assertEqual(report._get_report_currency(), "DOP")
        frappe.defaults.set_user_default("Company", self.company_name)

    def test_report_summary_uses_spanish_labels(self):
        report = DominicanRepublicSalesTaxReport({"company": self.company_name})
        report.registered_customers_total_sales = 100
        report.registered_customers_total_vat = 18
        report.unregistered_customers_total_sales = 50
        report.unregistered_customers_total_vat = 9

        summary = report.get_report_summary()

        labels = [entry["label"] for entry in summary]
        expected_labels = [
            "Ventas clientes registrados",
            "ITBIS clientes registrados",
            "Ventas clientes no registrados",
            "ITBIS clientes no registrados",
        ]
        self.assertEqual(labels, expected_labels)
        self.assertTrue(all(entry["currency"] == "USD" for entry in summary))

    def test_parse_filters_accepts_json_string(self):
        result = _parse_filters('{"company": "Test"}')
        self.assertIsInstance(result, frappe._dict)
        self.assertEqual(result.company, "Test")

    def test_parse_filters_handles_invalid_json(self):
        result = _parse_filters("{invalid")
        self.assertEqual(dict(result), {})
