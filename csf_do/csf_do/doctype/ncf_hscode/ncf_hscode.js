// Copyright (c) 2025, Navari Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on("NCF HSCode", {
	refresh(frm) {

	},

    item_tax(frm) {
        if (frm.doc.item_tax) {
            frappe.db.get_doc('Item Tax Template', frm.doc.item_tax)
                .then(template => {
                    if (template.taxes && template.taxes.length > 0) {
                        const first_tax_rate = template.taxes[0].tax_rate;
                        frm.set_value('itbis_', first_tax_rate);
                    } else {
                        frappe.msgprint(__('No taxes found in the selected Item Tax Template.'))
                    }
                });
        } else {
            frm.set_value('itbis_', 0)
        }
    }
});

frappe.listview_settings["NCF HSCode"] = {
    hide_name_column: true
}