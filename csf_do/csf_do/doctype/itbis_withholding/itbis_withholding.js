// Copyright (c) 2025, Navari Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on("ITBIS Withholding", {

    before_save(frm) {
        if (frm.doc.itbis_withholding_amount === frm.doc.outstanding_amount && !frm.doc.allocate_payment) {
            frm.set_value("allocate_payment", 1);
            frm.save();
            frm.refresh();
        }
    },

    company(frm) {
        frm.set_query("voucher_no", function () {
            return {
                filters: {
                    docstatus: 1,
                    company: frm.doc.company,
                },
            };
        });
    }
});