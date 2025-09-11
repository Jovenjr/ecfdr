frappe.ui.form.on('Sales Invoice', {
  refresh(frm) {
    if (!frm.doc.docstatus || frm.doc.docstatus !== 1) return;

    frm.add_custom_button(__('Enviar e-CF'), async () => {
      try {
        const { message } = await frappe.call({
          method: 'csf_do.csf_do.doctype.api.ecf_api.enviar_ecf_desde_sales_invoice',
          args: { name: frm.doc.name, tipo: '32' },
          freeze: true,
          freeze_message: __('Encolando envío e-CF...'),
        });
        frappe.show_alert({ message: __('Envío encolado'), indicator: 'green' });
      } catch (e) {
        frappe.msgprint({ title: __('Error'), message: e.message || e, indicator: 'red' });
      }
    });

    frm.add_custom_button(__('Consultar estado e-CF'), async () => {
      try {
        const { message } = await frappe.call({
          method: 'csf_do.csf_do.doctype.api.ecf_api.consultar_estado_desde_sales_invoice',
          args: { name: frm.doc.name },
          freeze: true,
          freeze_message: __('Consultando estado...'),
        });
        frappe.show_alert({ message: __('Consulta encolada'), indicator: 'blue' });
      } catch (e) {
        frappe.msgprint({ title: __('Error'), message: e.message || e, indicator: 'red' });
      }
    });

    frm.add_custom_button(__('Anular e-NCF'), async () => {
      try {
        const motivo = await new Promise((resolve) => {
          frappe.prompt(
            [{ fieldname: 'motivo', fieldtype: 'Small Text', label: __('Motivo de Anulación'), reqd: 0 }],
            (values) => resolve(values.motivo || ''),
            __('Anular e-NCF'),
            __('Continuar')
          );
        });
        const { message } = await frappe.call({
          method: 'csf_do.csf_do.doctype.api.ecf_api.anular_desde_sales_invoice',
          args: { name: frm.doc.name, motivo },
          freeze: true,
          freeze_message: __('Anulando e-NCF...'),
        });
        frappe.show_alert({ message: __('Solicitud de anulación enviada'), indicator: 'orange' });
      } catch (e) {
        frappe.msgprint({ title: __('Error'), message: e.message || e, indicator: 'red' });
      }
    });
  },
});


