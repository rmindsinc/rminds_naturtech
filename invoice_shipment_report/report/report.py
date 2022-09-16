from odoo import api, models




class ReportInvoiceWithPayment(models.AbstractModel):
    _inherit = 'report.account.report_invoice'

    @api.model
    def _get_report_values(self, docids, data=None):
        rslt = super()._get_report_values(docids, data)
        tracking_1 = ''
        carrier_1 = ''
        name_list = []
        for rec in rslt.get('docs'):
            picking_1 = self.env['stock.picking'].search([('origin', '=', rec.invoice_origin), ('state', '=', 'done'), ('name', 'like', 'OUT')])
            if picking_1:
                for rec_1 in picking_1:
                    if rec_1.carrier_id.name:
                        if rec_1.carrier_id.name not in name_list:
                            name_list.append(rec_1.carrier_id.name)
                    if rec_1.carrier_tracking_ref:
                        tracking_1 += str(rec_1.carrier_tracking_ref) + ', '
                if name_list:
                    if len(name_list) > 1:
                        for name in name_list:
                            carrier_1 += name + ', '
                    if len(name_list) == 1:
                        carrier_1 = name_list[0] + ', '
        tracking_1 = str(tracking_1)[:-2]
        carrier_1 = str(carrier_1)[:-2]
        print(tracking_1,"trackkkkkkkkkkkkkkkkkkk",carrier_1)


        val={'car':carrier_1,'trac':tracking_1}

        rslt['carrier'] = val
        return rslt