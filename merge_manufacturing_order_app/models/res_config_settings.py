# -*- coding: utf-8 -*-

from odoo import api, fields, models,_


class ResConfigSettingss(models.TransientModel):
	_inherit = 'res.config.settings'

	merge_manufacture_order = fields.Boolean(
		related='company_id.merge_manufacture_order',
		string="Merge Manufacturing Order",
		readonly=False
	)
	by_partner = fields.Boolean(
		related='company_id.by_partner',
		string="By Partner",
		readonly=False
	)
	by_duration = fields.Selection(
		related='company_id.by_duration',
		string="By Duration",
		readonly=False
	)

