from odoo import fields, models,api
from datetime import timedelta,date
import datetime

class ResPartner(models.Model):
    _inherit = "res.partner"

    review_required = fields.Boolean('Review Required',tracking=True)
    last_reviewed = fields.Date('Last Reviewed Date',default=date.today(),tracking=True)
    next_review = fields.Date('Next Review Date',readonly=True,compute="_autofill_date",store=True,tracking=True)
    next_alert = fields.Date('Next Reminder Date',readonly=True,compute="_reminder_date",store=True,tracking=True)
    vendor_ids = fields.One2many("vendor.review.log","vendor_id",tracking=True)
   

    @api.model
    def default_get(self, fields):
        res = super(ResPartner,self).default_get(fields)
        search_partner_mode = self.env.context.get('res_partner_search_mode')
        is_customer = search_partner_mode == 'customer'
        is_supplier = search_partner_mode == 'supplier'
        
        if is_customer and search_partner_mode:
            res.update({
                'review_required': False,
            })
        else:
            res.update({
                'review_required': True,
            })
        return res

    @api.depends("last_reviewed")
    def _autofill_date(self):
        purchase_rec = self.env['res.config.settings'].default_get([])
        execute_every_year = purchase_rec['execute_every_year']
        for rec in self:
            rec.next_review = rec.last_reviewed + timedelta(days = execute_every_year)

    @api.depends("next_review")
    def _reminder_date(self):
        purchase_rec = self.env['res.config.settings'].default_get([])
        trigger_before_days = purchase_rec['trigger_before_days']
        execute_every_year = purchase_rec['execute_every_year']
        for rec in self:
            rec.next_alert = rec.next_review - timedelta(days = trigger_before_days)
            