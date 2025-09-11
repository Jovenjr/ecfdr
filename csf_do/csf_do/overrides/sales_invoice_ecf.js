frappe.ui.form.on('Sales Invoice', {
    refresh(frm) {
        if (!frm.doc.docstatus || frm.doc.docstatus !== 1) return;

        // Estado badge from latest linked e-CF if any
        frappe.db.get_list('e-CF', {
            fields: ['name', 'estado_dgii'],
            filters: { sales_invoice: frm.doc.name },
            order_by: 'modified desc',
            limit: 1
        }).then(list => {
            if (list && list.length) {
                const rec = list[0];
                frm.dashboard.add_badge({ label: 'e-CF: ' + (rec.estado_dgii || '-'), color: 'blue' });
                frm.__ecf_name = rec.name;
            }
        });

        // Send e-CF button
        frm.add_custom_button('Enviar e-CF', () => {
            frappe.prompt([
                {label: 'Tipo e-CF', fieldname: 'tipo', fieldtype: 'Select', options: '31\n32\n33\n34\n41\n43\n44\n45\n46\n47', reqd: 1},
                {label: 'Documento e-CF', fieldname: 'ecf_name', fieldtype: 'Link', options: 'e-CF', reqd: 1, default: frm.__ecf_name}
            ], (vals) => {
                frappe.call({
                    method: 'csf_do.csf_do.doctype.api.ecf_api.enviar_ecf',
                    args: { name: vals.ecf_name, tipo: vals.tipo },
                }).then(() => frappe.show_alert('Envío e-CF encolado'));
            }, 'Enviar e-CF');
        }, 'e-CF');

        // Consult status button
        frm.add_custom_button('Consultar Estado e-CF', () => {
            const ecf_name = frm.__ecf_name;
            if (!ecf_name) { frappe.msgprint('No hay e-CF vinculado.'); return; }
            frappe.call({
                method: 'csf_do.csf_do.doctype.api.ecf_api.consultar_estado',
                args: { name: ecf_name },
            }).then(() => frappe.show_alert('Consulta encolada'));
        }, 'e-CF');
    }
});

