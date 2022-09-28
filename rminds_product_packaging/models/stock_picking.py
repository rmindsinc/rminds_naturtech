from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def action_put_in_pack(self):
        res = super(StockPicking, self).action_put_in_pack()
        return res


class MoveLine(models.Model):
    _inherit = 'stock.move.line'

    packaging_qty = fields.Integer("Packaging Qty", readonly=True)
    packaging_type = fields.Char("Packaging Type", readonly=True)

    def write(self, vals):
        for item in self:
            if 'result_package_id' in vals and vals['result_package_id'] and item.picking_id and item.picking_id.sale_id:
                for line in item.picking_id.sale_id.order_line:
                    if line.product_id.id == item.product_id.id:
                        if line.product_packaging_id:
                            package_qty = line.product_packaging_id.qty
                            total_cases = item.qty_done/package_qty
                            integer_total = int(total_cases)
                            if total_cases > integer_total:
                                integer_total = integer_total + 1
                            item.packaging_qty = integer_total
                            item.packaging_type = line.product_packaging_id.package_type_id.name
        return super(MoveLine, self).write(vals)
