# Copyright 2020-2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models,api


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    overdue_reminder_attach_invoice = fields.Boolean(
        related="company_id.overdue_reminder_attach_invoice", readonly=False
    )
    overdue_reminder_start_days = fields.Integer(
        related="company_id.overdue_reminder_start_days", readonly=False
    )
    overdue_reminder_min_interval_days = fields.Integer(
        related="company_id.overdue_reminder_min_interval_days", readonly=False
    )
    overdue_reminder_interface = fields.Selection(
        related="company_id.overdue_reminder_interface", readonly=False
    )
    overdue_reminder_partner_policy = fields.Selection(
        related="company_id.overdue_reminder_partner_policy", readonly=False
    )

    overdue_limit_counter = fields.Integer(string="Counter Limit", readonly=False)
    mail_reminder_days = fields.Integer(string="Mail Reminder After Days", readonly=False)
    user_id = fields.Many2one('res.users', string='Approval Name', config_parameter="account_invoice_overdue_reminder.user_id",require=True)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        res.update(
            overdue_limit_counter=int(params.get_param('account_invoice_overdue_reminder.overdue_limit_counter', default=3)),
            mail_reminder_days=int(params.get_param('account_invoice_overdue_reminder.mail_reminder_days', default=5))
        )
        return res  

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param("account_invoice_overdue_reminder.overdue_limit_counter", self.overdue_limit_counter)
        self.env['ir.config_parameter'].sudo().set_param("account_invoice_overdue_reminder.mail_reminder_days", self.mail_reminder_days)
    