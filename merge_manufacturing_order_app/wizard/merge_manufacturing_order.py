# -*- coding: utf-8 -*-

from odoo import api, fields, models,_
from odoo.exceptions import UserError, AccessError


class Merge_MO(models.TransientModel):
	_name = 'merge.mo'
	_description = 'Merged Manufacturing Order'

	merge_partner = fields.Selection([
		('merge_by_partner', 'Merge Based On  Partner'),
		('merge_by_duration', 'Merge Based On Duration'),
		], "Merge By Partner", default="merge_by_partner")
	by_duration = fields.Selection([
			('day', 'Day'),
			('week', 'Week'),
			('month', 'Month'),
		],default='day',string="Merge By Duration")

	def merged_mo(self):
		if self.merge_partner == 'merge_by_duration':
			if self.by_duration == 'day':
				self.wizard_day_cron_job()
			elif self.by_duration == 'week':
				self.wizard_week_cron_job()
			elif self.by_duration == 'month':
				self.wizard_month_cron_job()
		else:
			self.day_cron_job()
	
	def wizard_day_cron_job(self):
		active_id=self._context.get('active_id')
		active_ids = self._context.get('active_ids')
		mo_obj = self.env['mrp.production']
		mo_order_ids = mo_obj.browse(self.env.context['active_ids'])
		if not mo_order_ids or len(mo_order_ids) == 1:
			return 
		first_mo = mo_order_ids[0]
		product_id = first_mo.product_id.id
		bom_id = first_mo.bom_id.id
		result = [manufacturing_order for manufacturing_order in mo_order_ids if manufacturing_order.product_id.id > product_id] or  [manufacturing_order for manufacturing_order in mo_order_ids if manufacturing_order.product_id.id < product_id]
		state_res = [manufacturing_order for manufacturing_order in mo_order_ids if manufacturing_order.state != 'draft']
		
		if len(result):
			raise UserError(
				_('Found Different  Products !\n\n You can only allow to merge same product'))
			
		if len(state_res):
			raise UserError(
				_('Found Different State !\n\n You can only allow to merge MO with draft status.'))
		total_qty = 0
		new_mo = mo_order_ids[0].copy()
		ref = ''
		for manufacturing_order in mo_order_ids:
			total_qty += manufacturing_order.product_qty
			if not ref: 
				ref = manufacturing_order.origin
			else:
				ref += ', '+str(manufacturing_order.origin)		
		new_mo.write({'product_qty':total_qty, 'origin': ref})
		new_mo._onchange_product_id()
		new_mo._onchange_move_raw()
		mo_order_ids.write({'state':'cancel'})


	def wizard_week_cron_job(self):	
		active_id=self._context.get('active_id')
		active_ids = self._context.get('active_ids')
 
		mo_obj = self.env['mrp.production']
		mo_order_ids = mo_obj.browse(self.env.context['active_ids'])
		if not mo_order_ids or len(mo_order_ids) == 1:
			return 
		first_mo = mo_order_ids[0]
		product_id = first_mo.product_id.id
		bom_id = first_mo.bom_id.id
		result = [manufacturing_order for manufacturing_order in mo_order_ids if manufacturing_order.product_id.id > product_id] or  [manufacturing_order for manufacturing_order in mo_order_ids if manufacturing_order.product_id.id < product_id]
		state_res = [manufacturing_order for manufacturing_order in mo_order_ids if manufacturing_order.state != 'draft']
		if len(result):
			raise UserError(
				_('Found Different  Products !\n\n You can only allow to merge same product'))
			
		if len(state_res):
			raise UserError(
				_('Found Different State !\n\n You can only allow to merge MO with draft status.'))
		total_qty = 0
		new_mo = mo_order_ids[0].copy()
		ref = ''
		for manufacturing_order in mo_order_ids:
			total_qty += manufacturing_order.product_qty
			if not ref: 
				ref = manufacturing_order.origin
			else:
				ref += ', '+str(manufacturing_order.origin)		
		new_mo.write({'product_qty':total_qty, 'origin': ref})
		new_mo._onchange_product_id()
		new_mo._onchange_move_raw()
		mo_order_ids.write({'state':'cancel'})


	def wizard_month_cron_job(self):
		active_id=self._context.get('active_id')
		active_ids = self._context.get('active_ids')
		active_model = self._context.get('active_model')
		browse_id=self.env[active_model].browse(active_id)  
			
		mo_obj = self.env['mrp.production']
		mo_order_ids = mo_obj.browse(self.env.context['active_ids'])
		if not mo_order_ids or len(mo_order_ids) == 1:
			return 
		first_mo = mo_order_ids[0]
		product_id = first_mo.product_id.id
		bom_id = first_mo.bom_id.id
		result = [manufacturing_order for manufacturing_order in mo_order_ids if manufacturing_order.product_id.id > product_id] or  [manufacturing_order for manufacturing_order in mo_order_ids if manufacturing_order.product_id.id < product_id]
		state_res = [manufacturing_order for manufacturing_order in mo_order_ids if manufacturing_order.state != 'draft']
		
		if len(result):
			raise UserError(
				_('Found Different  Products !\n\n You can only allow to merge same product'))
			
		if len(state_res):
			raise UserError(
				_('Found Different State !\n\n You can only allow to merge MO with draft status.'))
		total_qty = 0
		new_mo = mo_order_ids[0].copy()
		ref = ''
		for manufacturing_order in mo_order_ids:
			total_qty += manufacturing_order.product_qty

			if not ref: 
				ref = manufacturing_order.origin
			else:
				ref += ', '+str(manufacturing_order.origin)		
		new_mo.write({'product_qty':total_qty, 'origin': ref})
		new_mo._onchange_product_id()
		new_mo._onchange_move_raw()
		mo_order_ids.write({'state':'cancel'})


	def day_cron_job(self):
		active_id=self._context.get('active_id')
		active_ids = self._context.get('active_ids')			
		mo_obj = self.env['mrp.production']
		mo_order_ids = mo_obj.browse(self.env.context['active_ids'])
		if not mo_order_ids or len(mo_order_ids) == 1:
			return 
		first_mo = mo_order_ids[0]
		product_id = first_mo.product_id.id
		partner_id = first_mo.partner_id.id
		bom_id = first_mo.bom_id.id
		result2 = [manufacturing_order for manufacturing_order in mo_order_ids if manufacturing_order.partner_id.id < partner_id] or[manufacturing_order for manufacturing_order in mo_order_ids if manufacturing_order.partner_id.id > partner_id]		
		result = [manufacturing_order for manufacturing_order in mo_order_ids if manufacturing_order.product_id.id > product_id] or  [manufacturing_order for manufacturing_order in mo_order_ids if manufacturing_order.product_id.id < product_id]
		state_res = [manufacturing_order for manufacturing_order in mo_order_ids if manufacturing_order.state not in ('draft','confirmed')]
		if len(result2):
			raise UserError(
				_('Found Different FG customer !\n\n You can only allow to merge same customer')) 	
		if len(result):
			raise UserError(
				_('Found Different  Products !\n\n You can only allow to merge same product'))
		if len(state_res):
			raise UserError(
				_('Found Different State !\n\n You can only allow to merge MO with draft or confirm status.'))
		total_qty = 0
		new_mo = mo_order_ids[0].copy()
		ref = ''
		for manufacturing_order in mo_order_ids:
			total_qty += manufacturing_order.product_qty	
			if not ref: 
				ref = manufacturing_order.origin
			else:
				ref += ', '+str(manufacturing_order.origin)		
		new_mo.write({'product_qty':total_qty, 'origin': ref})
		new_mo._onchange_product_id()
		new_mo._onchange_move_raw()
		mo_order_ids.write({'state':'cancel'})





