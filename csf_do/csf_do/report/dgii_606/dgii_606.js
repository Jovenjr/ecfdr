frappe.query_reports["DGII 606"] = {
	onload: function(report) {
		report.page.add_inner_button(__('Exportar DGII (CSV)'), function() {
			const filters = report.get_values();
			frappe.call({
				method: 'csf_do.csf_do.report.dgii_606.dgii_606.export_csv',
				args: { filters: filters },
				callback: function(r) {
					if (r && r.message && r.message.file_url) {
						window.open(r.message.file_url);
					} else {
						frappe.msgprint(__('No se pudo generar el archivo CSV.'));
					}
				}
			});
		});
	}
};

