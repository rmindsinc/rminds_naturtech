from odoo import api, fields, models,_
from odoo.exceptions import ValidationError

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    trigger_before_days = fields.Integer()
    execute_every_year = fields.Integer()

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        res.update(
            trigger_before_days=int(params.get_param('rminds_vendor_review.trigger_before_days', default=7)),
            execute_every_year=int(params.get_param('rminds_vendor_review.execute_every_year', default=365)),
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param("rminds_vendor_review.trigger_before_days", self.trigger_before_days)
        self.env['ir.config_parameter'].sudo().set_param("rminds_vendor_review.execute_every_year", self.execute_every_year)


class VendorReviewConfig(models.Model):
    _name = 'vendor.review.config'
    _description = 'Vendor Review Notification Config'

    # pact_act_approval = fields.Selection([('notification_for_approval', 'Notification for Approval')],
    #                                      string='Notification for Approval', required=True)
    user_id = fields.Many2many('res.users', string='Recipients', required=True)

    '''
    	Overrided create method to restrict user from creating multiple records in config menu.
    	'''

    @api.model
    def create(self, vals):
        config_rec_id = self.env['vendor.review.config'].sudo().search([])
        if config_rec_id:
            if len(config_rec_id) > 0:
                raise ValidationError(
                    _('You cannot create multiple configuration record. Please update the existing one'))
        res = super(VendorReviewConfig, self).create(vals)
        return res