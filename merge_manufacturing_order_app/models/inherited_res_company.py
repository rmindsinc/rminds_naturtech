# -*- coding: utf-8 -*-


from odoo import fields, models

class Company(models.Model):
	_inherit = 'res.company'

	merge_manufacture_order = fields.Boolean(string="Merge Manufacturing Order")
	by_partner = fields.Boolean(string="By Partner")
	by_duration = fields.Selection([
			('day', 'Day'),
			('week', 'Week'),
			('month', 'Month'),
		], string="By Duration")
