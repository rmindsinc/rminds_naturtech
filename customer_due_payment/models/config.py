from odoo import api, fields, models, _

class AccountConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    overdue_msg = fields.Text(related='company_id.overdue_msg', string='Overdue Payments Message *')