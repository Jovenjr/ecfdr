// Copyright (c) 2025, AI Studio RD and contributors
// For license information, please see license.txt

frappe.query_reports["IT-1 Declaracion Jurada"] = {
	"filters": [
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.datetime.month_start(),
			reqd: 1
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.datetime.month_end(),
			reqd: 1
		},
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company")
		},
		{
			fieldname: "supplier",
			label: __("Supplier"),
			fieldtype: "Link",
			options: "Supplier"
		}
	],
	
	onload: function(report) {
		// Botón para exportar a Excel
		report.page.add_inner_button(__("Export to Excel"), function() {
			const filters = report.get_values();
			frappe.call({
				method: "csf_do.csf_do.report.it_1_declaracion_jurada.it_1_declaracion_jurada.export_to_excel",
				args: {
					filters: filters
				},
				callback: function(r) {
					if (r.message) {
						window.open(frappe.urllib.get_full_url(
							"/api/method/frappe.core.doctype.file.file.download_file"
							+ "?file_url=" + encodeURIComponent(r.message)
						));
					}
				}
			});
		});
		
		// Mostrar resumen
		report.page.add_inner_button(__("Show Summary"), function() {
			const filters = report.get_values();
			frappe.call({
				method: "csf_do.csf_do.report.it_1_declaracion_jurada.it_1_declaracion_jurada.get_summary",
				args: {
					filters: filters
				},
				callback: function(r) {
					if (r.message) {
						frappe.msgprint({
							title: __("IT-1 Summary"),
							message: `
								<div style="font-size: 14px;">
									<p><b>Total Facturas:</b> ${r.message.total_facturas}</p>
									<p><b>Total Facturado:</b> ${format_currency(r.message.total_facturado)}</p>
									<p><b>ITBIS Facturado:</b> ${format_currency(r.message.total_itbis_facturado)}</p>
									<p><b>ITBIS Retenido:</b> ${format_currency(r.message.total_itbis_retenido)}</p>
								</div>
							`
						});
					}
				}
			});
		});
	}
};
