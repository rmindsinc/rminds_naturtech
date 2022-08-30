from odoo import fields, models,api
from datetime import timedelta,date
import datetime
import pytz
from datetime import timezone

class VendorReviewLog(models.Model):
    _name = "vendor.review.log"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Vendor Review Log  History"

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
        vender_result = self.env["res.partner"].search([("review_required","=",True)])
    
        template_xmlid = "rminds_vendor_review.vendor_review_log_mail_template"
        mail_tpl = self.env.ref(template_xmlid)
        
        for rec in vender_result:
            if rec.next_alert == date.today():
                tmpl_lang = mail_tpl.with_context(lang=rec.lang or "en_US")
                mail_data = tmpl_lang.generate_email(
                    rec.id, ['subject', 'body_html', 'email_from', 'email_to',
                    'email_cc', 'reply_to', 'scheduled_date', 'attachment_ids'])
                vals={
                    "subject": self.env.company.name,
                    "body_html": mail_data.get('body_html'),
                    'email_from': self.env.company.partner_id.email,
                    # 'email_to': rec.email,
                    'recipient_ids': [rec.id],
                    'model':'res.partner',
                    'res_id':rec.id,
                    'record_name':rec.name
                }
                mail_id = mail_obj.create(vals)
                mail_obj.send(mail_id)