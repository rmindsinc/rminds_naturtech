from odoo import fields, models,api

class VendorReviewMasterLog(models.Model):
    _name = "vendor.review.master.log"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Vendor Review Master Log  History"

    notified_date = fields.Date('Date',tracking=True)
    notified_email = fields.Boolean('Email Notified',default=False,tracking=True)
    log_ids = fields.One2many("vendor.review.log","master_id",tracking=True)