from odoo import fields,api,models,_
from odoo.exceptions import ValidationError
from datetime import date

class ProductTemplate(models.Model):
    _inherit = 'account.move'

    def list_due_invoices(self):
        today = fields.Date.context_today(self)
        invoice_args = [

            ('invoice_date_due', '<=', today),
            ('move_type', '=', 'in_invoice'),
            ('payment_state', 'not in', ("paid", "reversed", "in_payment")),
            ('state', '=', 'posted'),
        ]
        invoices = self.env['account.move'].search(invoice_args)
        inv_context = {"inv_id": []};

        for invoice in invoices:

            rec =inv_context["inv_id"].append(invoice)

        if len(inv_context['inv_id']) > 0:

            receipt_id = []
            recip_obj = self.env['vendor.due.config'].sudo().search([])
            for rec in recip_obj.user_id:
                receipt_id.append(rec.partner_id.id)

            template_obj = self.env.ref('rminds_vendor_due_bills.mail_template_vendor_due')
            mail = template_obj.with_context(inv_context).with_user(2).send_mail(self.id, email_values={'recipient_ids': receipt_id})



# class ResConfigSettings(models.TransientModel):
#     _inherit = "res.config.settings"
#
#     notify_user = fields.Many2one('res.users', string='Notify User', require=True)
#
#
#     @api.model
#     def get_values(self):
#         res = super(ResConfigSettings, self).get_values()
#         params = self.env['ir.config_parameter'].sudo()
#         notify_user = params.get_param('rminds_vendor_due_bills.notify_user', default=False)
#
#         res.update(
#             notify_user=int(notify_user),
#         )
#         return res
#
#     def set_values(self):
#         super(ResConfigSettings, self).set_values()
#         self.env['ir.config_parameter'].sudo().set_param("rminds_vendor_due_bills.notify_user", self.notify_user.id)

class VendorDueConfig(models.Model):
    _name = 'vendor.due.config'
    _description = 'Vendor Due Notification Config'

    user_id = fields.Many2many('res.users', string='Recipients', required=True)

    '''
    	Overrided create method to restrict user from creating multiple records in config menu.
    	'''

    @api.model
    def create(self, vals):
        config_rec_id = self.env['vendor.due.config'].sudo().search([])
        if config_rec_id:
            if len(config_rec_id) > 0:
                raise ValidationError(
                    _('You cannot create multiple configuration record. Please update the existing one'))
        res = super(VendorDueConfig, self).create(vals)
        return res
