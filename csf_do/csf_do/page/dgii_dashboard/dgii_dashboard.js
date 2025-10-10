frappe.pages['dgii-dashboard'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Dashboard DGII',
		single_column: true
	});

	// Cargar el HTML del dashboard
	$(frappe.render_template("dgii_dashboard", {})).appendTo(page.body);
}
