from odoo import models,fields,api



class MrpBom(models.Model):

    _inherit = 'mrp.bom'

    is_percentage = fields.Boolean("Component By %")

    @api.onchange('product_qty', 'is_percentage')
    def _onchange_product_qty(self):
        if self.is_percentage == True:
            for line in self.bom_line_ids:
                if line.bom_percentage > 0:
                    line._compute_qty()




class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    bom_percentage = fields.Float(string="Percentage",default=0,
                                       help='The percentage in between 1 and 100')


    @api.onchange('bom_percentage')
    def _compute_qty(self):

        if self.bom_id.is_percentage == True:
            for line in self:
                if line.bom_percentage > 0:
                    qty = (line.bom_percentage * line.bom_id.product_qty)
                    line.product_qty = qty
