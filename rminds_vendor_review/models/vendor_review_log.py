from odoo import fields, models,api
from datetime import timedelta,date
import datetime
import pytz
from datetime import timezone

class VendorReviewLog(models.Model):
    _name = "vendor.review.log"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Vendor Review Log  History"
    _rec_name = 'id'

    vendor_id = fields.Many2one("res.partner",tracking=True)
    master_id = fields.Many2one("vendor.review.master.log",tracking=True)
    mail_triggered_date = fields.Date("Mail Triggered Date",tracking=True)
    last_reviewed_date = fields.Date('Last Reviewed Date',tracking=True)
    status = fields.Selection(
        selection=[
            ('draft','Draft'),
            ('reviewed','Reviewed'),
        ],required=True, default="draft",string="Status",tracking=True
    )

    def auto_vendor_review(self):
        mail_obj = self.env['mail.mail']        
        vender_result = self.env["res.partner"].search([("review_required","=",True),('next_alert','<=', date.today())])
        receipt_id = []
        recip_obj = self.env['vendor.review.config'].sudo().search([])
        for rec in recip_obj.user_id:
            receipt_id.append(rec.partner_id.id)

        if vender_result:
            template_obj = self.env.ref('rminds_vendor_review.vendor_review_log_mail_template')
            mail=template_obj.with_user(2).send_mail(self.id ,email_values={'recipient_ids': receipt_id}, )
            if mail:
                for rec in vender_result:
                    log_detail = {
                            'vendor_id':rec.id,
                            'mail_triggered_date': date.today(),
                            'last_reviewed_date': rec.last_reviewed,
                            'status': 'draft'

                        }
                    if len(log_detail):
                        self.create(log_detail)
