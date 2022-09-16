from odoo import models,fields,api,_
from odoo.exceptions import UserError

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def action_product_last_five_inv_price(self):
        action = self.env.ref('po_last_five_invoice_products.action_invoice_last_inv_price_form').read()[0]
        action.update({'domain': [('product_id', '=', self.product_id.id),('state','in',('draft','posted')),('move_type','=','in_invoice')], 'name': 'Last 5 invoice price for '+ self.product_id.name})
        # import pdb;pdb.set_trace()
        return action


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    # vendor_id = fields.Many2one('res.partner','Vendor', compute="compute_vendor_id",store=False)
    vendor_id = fields.Many2one('res.partner','Vendor', related="move_id.partner_id",store=True)
    # state = fields.Selection([
    #     ('draft', 'Draft'),
    #     ('posted', 'Posted'),
    #     ('cancel', 'cancelled'),
    # ], compute="compute_state",store=False)
    state = fields.Selection(related='move_id.state', store=True)
    move_type = fields.Selection(related='move_id.move_type', store=True)

    # @api.depends('move_id.partner_id')
    # def compute_vendor_id(self):
    #     for res in self:
    #         res.vendor_id =  res.move_id.partner_id

    # @api.depends('move_id.state')
    # def compute_state(self):
    #     for res in self:
    #         res.state = res.move_id.state

class AccountMove(models.Model):
    _inherit = "account.move"

    def get_payment_request_url(self):
        vals = {
            'res_id': self.id,
            'res_model': 'account.move',
            'description': self.payment_reference,
            'amount': self.amount_residual,
            'currency_id': self.currency_id.id,
            'partner_id': self.partner_id.id,
        }
        plw = self.env['payment.link.wizard'].sudo().create(vals)
        return plw.link