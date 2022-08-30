from odoo import api, fields, models

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