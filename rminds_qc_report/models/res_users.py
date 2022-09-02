from odoo import fields,models


class Users(models.Model):
	_inherit = 'res.users'

	is_lab_user = fields.Boolean('Lab User')