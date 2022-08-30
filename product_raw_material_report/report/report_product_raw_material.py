from odoo import api, fields, models
from datetime import datetime

class ReportProductRaw(models.AbstractModel):
    _name = 'report.product_raw_material_report.report_raw'

    @api.model
    def _get_report_values(self, docids, data=None):
        print ("Called")
        # wiz_rec = self.env[self._context.get('active_model', False)].browse(self._context.get('active_id', False))
        wiz_rec = self.env['product.product'].browse(data['product_id'])
        # report = self.env['ir.actions.report']._get_report_from_name('product_raw_material_report.report_raw')
        # docids = self.env[report.model].browse(docids)
        user = self.env.user
        bom_lines = self.env['mrp.bom.line'].search([('product_id','=',data['product_id'])])
        bom_list = []
        if bom_lines:
            for bom in bom_lines:
                bom_list.append(bom.bom_id)
        return {
            'doc_ids': wiz_rec,
            'docs': wiz_rec,
            'Date': fields.date.today(),
            'user':user,
            'date_from':datetime.strptime(data['date_from'], '%Y-%m-%d'),
            'date_to':datetime.strptime(data['date_to'], '%Y-%m-%d'),
            'product_name':wiz_rec.display_name,
            'bom_list':bom_list
        }