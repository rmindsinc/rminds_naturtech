from odoo import fields, models,api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'


    price_diff_percentage = fields.Float("Price price difference warning percentage")

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param('purchase_order_line.price_diff_percentage', self.price_diff_percentage)
        return res


    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        value = self.env['ir.config_parameter'].sudo().get_param('purchase_order_line.price_diff_percentage')
        # google_provider = self.env.ref('auth_oauth.provider_google', False)
        res.update(
            # auth_oauth_google_enabled=google_provider.enabled,
            # auth_oauth_google_client_id=google_provider.client_id,
            # server_uri_google=self.get_uri(),
            price_diff_percentage =  value
        )
        return res