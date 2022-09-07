# -*- coding: utf-8 -*-
from ast import literal_eval
from distutils.command.check import check

from odoo import api, models, fields, _
from odoo.exceptions import UserError


class QualityCheck(models.Model):
    _inherit = 'quality.check'

    def get_worksheet(self):
        worksheet = self.env[self.worksheet_template_id.model_id.sudo().model].search(
            [('x_quality_check_id', '=', self.id)])
        print(worksheet.read(), "\n Worksheet ===================")
        return worksheet

