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

        // Send e-CF button (desde Sales Invoice)
        frm.add_custom_button('Enviar e-CF', () => {
            frappe.prompt([
                {label: 'Tipo e-CF', fieldname: 'tipo', fieldtype: 'Select', options: '31\n32\n33\n34\n41\n43\n44\n45\n46\n47', reqd: 1}
            ], (vals) => {
                frappe.call({
                    method: 'csf_do.csf_do.doctype.api.ecf_api.enviar_ecf_desde_sales_invoice',
                    args: { name: frm.doc.name, tipo: vals.tipo },
                }).then(() => frappe.show_alert('Envío e-CF encolado desde Sales Invoice'));
            }, 'Enviar e-CF');
        }, 'e-CF');

        // RFCE (Resumen Factura Consumo) - Envío mínimo a partir de la factura
        frm.add_custom_button('Enviar RFCE 32', () => {
            // Construcción mínima: reutiliza datos de la factura para RFCE
            frappe.call({
                method: 'frappe.call',
                args: {
                    method: 'csf_do.csf_do.utils.ecf_service.enviar_rfce32',
                    args: {
                        data: {
                            encabezado: {
                                Version: '1.0',
                                IdDoc: {
                                    TipoeCF: '32', eNCF: frm.doc.__encf || 'E320000000001', TipoIngresos: '1', TipoPago: (frm.doc.outstanding_amount && Math.abs(frm.doc.outstanding_amount) > 0.01) ? '2' : '1'
                                },
                                Emisor: {
                                    RNCEmisor: frm.doc.company_tax_id || '', RazonSocialEmisor: frm.doc.company, FechaEmision: frm.doc.posting_date
                                },
                                Comprador: { RNCComprador: frm.doc.tax_id || '', RazonSocialComprador: frm.doc.customer_name },
                                Totales: { MontoTotal: String(frm.doc.grand_total || frm.doc.base_grand_total || 0) }
                            },
                            CodigoSeguridadeCF: frm.doc.__codigo_seguridad || 'ABCDEF'
                        },
                        base_url: 'mock://precert', cert_path: '', key_path: ''
                    }
                }
            }).then(() => frappe.show_alert('RFCE 32 enviado (mock)'));
        }, 'e-CF');

        frm.add_custom_button('Consultar Resumen RFCE', () => {
            frappe.call({
                method: 'frappe.call',
                args: { method: 'csf_do.csf_do.utils.ecf_service.consultar_resumen_rfce32', args: { base_url: 'mock://precert' } }
            }).then(r => {
                frappe.msgprint(__('Respuesta RFCE: {0}', [JSON.stringify(r && r.message || {}, null, 2)]));
            });
        }, 'e-CF');
        // Consult status button (desde Sales Invoice)
        frm.add_custom_button('Consultar Estado e-CF', () => {
            frappe.call({
                method: 'csf_do.csf_do.doctype.api.ecf_api.consultar_estado_desde_sales_invoice',
                args: { name: frm.doc.name },
            }).then(() => frappe.show_alert('Consulta encolada'));
        }, 'e-CF');

        // Anular e-NCF
        frm.add_custom_button(__('Anular e-NCF'), () => {
            frappe.prompt([
                { fieldname: 'motivo', fieldtype: 'Small Text', label: __('Motivo de Anulación'), reqd: 0 }
            ], (vals) => {
                frappe.call({
                    method: 'csf_do.csf_do.doctype.api.ecf_api.anular_desde_sales_invoice',
                    args: { name: frm.doc.name, motivo: vals.motivo },
                }).then(() => {
                    frappe.show_alert({ message: __('Solicitud de anulación enviada'), indicator: 'orange' });
                });
            }, __('Anular e-NCF'));
        }, 'e-CF');
    }
});


