from odoo import models,fields,api,_
from odoo.exceptions import UserError

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    price_diff_percentage = fields.Float("Price price difference warning percentage")

    def action_product_last_five_inv_price(self):
        value = self.env['ir.config_parameter'].sudo().get_param('purchase_order_line.price_diff_percentage')
        # import pdb;pdb.set_trace()
        res = self.env['account.move.line'].search([('product_id', '=', self.product_id.id), ('move_type','=','in_invoice'),('vendor_id','=',self.partner_id.id),('state','in',('draft','posted'))],limit=2, order='create_date desc')
        
        if value and self.product_id and len(res) == 2:
            if res[0].price_unit - res[1].price_unit >= (res[0].price_unit * float(value) / 100):
                raise UserError(_("Invoice Price changed for "+ self.product_id.name + " from " + str(res[1].price_unit) + " to " + str(res[0].price_unit)))
            else:
                raise UserError(_("No Changes in invoice price for given difference percentage"))
        else:
            raise UserError(_("No Changes in invoice price for this product"))
        

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    vendor_id = fields.Many2one('res.partner','Vendor', related="move_id.partner_id",store=True)
    state = fields.Selection(related='move_id.state', store=True)
    move_type = fields.Selection(related='move_id.move_type', store=True)
