# -*- coding: utf-8 -*-

import time
from datetime import datetime
from dateutil import relativedelta
from odoo import api, models, fields, _

class ProductRawWizard(models.TransientModel):
    _name = "product.raw.wizard"

    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True
    )
    date_from = fields.Date(
        string='Start Date',
        required=True
    )
    date_to = fields.Date(
        string='End Date',
        required=True
    )

    def action_print_report(self):
        product_id = self.product_id
        data = {
            'date_from': self.date_from,
            'date_to': self.date_to,
            'product_id': self.product_id.id
        }
        return self.env.ref(
            'product_raw_material_report.action_report_product_raw'
        ).report_action(self, data=data)