# -*- coding: utf-8 -*-
from ast import literal_eval
from distutils.command.check import check

from odoo import api, models, fields, _
from odoo.exceptions import UserError


class QualityCheck(models.Model):
    _inherit = 'quality.check'

    def get_worksheet(self):
        worksheet = False
        wk_records = self.production_id.related_captured_templates
        wk_records = wk_records.split("@@")
        for item in wk_records:
            if item:
                try:
                    data = item.split('##')
                    model, id, template_for = data[0], data[1], data[2]
                    rec = self.env[model].sudo().browse(int(id))
                    if template_for == 'mixing':
                        worksheet = rec
                except:
                    pass

        if not worksheet:
            try:
                worksheet = self.env[self.worksheet_template_id.model_id.sudo().model].search(
                    [('x_quality_check_id', '=', self.id)])
            except:
                print("ok")

        print (worksheet, 'WORKSHEET =======================')
        return worksheet


