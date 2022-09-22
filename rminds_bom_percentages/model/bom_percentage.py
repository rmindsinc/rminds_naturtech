from odoo import models,fields,api



class MrpBom(models.Model):

    _inherit = 'mrp.bom'

    is_percentage = fields.Boolean("Component By %")

    @api.onchange('product_qty', 'is_percentage')
    def _onchange_product_qty(self):

        if self.is_percentage == True:
            for line in self.bom_line_ids:
                if line.bom_percentage > 0:
                    line._compute_qtys()




class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    bom_percentage = fields.Float(string="Percentage",default=0, digits=(16, 4), help='The percentage in between 1 and 100')
    percent_sign = fields.Char("", default="%")


    @api.onchange('bom_percentage')
    def _compute_qty(self):
        if self.bom_id.is_percentage == True:
            for line in self:
                if line.bom_percentage > 0:
                    qty = (line.bom_percentage * line.bom_id.product_qty)
                    line.product_qty = qty

    @api.onchange('product_qty')
    def _compute_qtys(self):

        if self.bom_id.is_percentage == True:
            for line in self:
                per = line.product_qty/line.bom_id.product_qty

                line.bom_percentage = per


class MrpProduction(models.Model):
    _inherit = 'stock.move'

    #mo_percentage = fields.Float(string="Percentage", compute="change_result")
    mo_percentage = fields.Float(string="Percentage", digits=(16, 4))
    percent_sign = fields.Char("", default="%")

    @api.depends('product_uom_qty','raw_material_production_id.product_qty')
    def change_result(self):
        for record in self:
            if record.product_uom_qty:
                try:
                    record.mo_percentage = record.product_uom_qty/record.raw_material_production_id.product_qty
                except:
                    record.mo_percentage = 0


class MRPProduction(models.Model):
    _inherit = 'mrp.production'

    is_percentage = fields.Boolean("Compound by %", compute='check_if_percentage')

    def check_if_percentage(self):
        for mo in self:
            if mo.bom_id.is_percentage:
                mo.is_percentage = True
            else:
                mo.is_percentage = False

