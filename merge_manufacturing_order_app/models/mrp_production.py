# -*- coding: utf-8 -*-
from odoo import api, models, fields, _
from odoo.exceptions import UserError, ValidationError
from psycopg2 import IntegrityError
import itertools
from odoo.addons.mrp.models.mrp_production import MrpProduction as mp
from odoo.tools.float_utils import float_compare, float_round, float_is_zero

class StockMove(models.Model):
    _inherit = "stock.move.line"

    company_id = fields.Many2one(
        'res.company', 'Company',
        default=lambda self: self.env.company,
        index=True)

# mrp.workorder
class MrpAbstractWorkorder(models.AbstractModel):
    _inherit = "mrp.workorder"

    def _update_finished_move(self):
        res=super(MrpAbstractWorkorder, self)   
        production_move = self.production_id.move_finished_ids.filtered(
            lambda move: move.product_id == self.product_id and
            move.state not in ('done', 'cancel')
        )
        if production_move and production_move.product_id.tracking != 'none':
            if not self.finished_lot_id:
                raise UserError(_('You need to provide a lot for the finished product.'))
            move_line = production_move.move_line_ids.filtered(
                lambda line: line.lot_id.id == self.finished_lot_id.id
            )
            if move_line:
                if self.product_id.tracking == 'serial':
                    raise UserError(_('You cannot produce the same serial number twice.'))
                move_line.product_uom_qty += self.qty_producing
                move_line.qty_done += self.qty_producing
            else:
                location_dest_id = production_move.location_dest_id._get_putaway_strategy(self.product_id).id or production_move.location_dest_id.id
                move_line.create({
                    'move_id': move_line.id,
                    'product_id': production_move.product_id.id,
                    'lot_id': self.finished_lot_id.id,
                    'product_uom_qty': self.qty_producing,
                    'product_uom_id': self.product_uom_id.id,
                    'qty_done': self.qty_producing,
                    'location_id': production_move.location_id.id,
                    'location_dest_id': location_dest_id,
                })
        else:
            rounding = production_move.product_uom.rounding
            production_move._set_quantity_done(
                float_round(self.qty_producing, precision_rounding=rounding)
            )
        return res


class StockMove(models.Model):
    _inherit = "stock.move"

    product_id = fields.Many2one(
        'product.product', 'Product',
        states={'confirmed': [('readonly', False)]})


class saleorderinherit(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        result= super(saleorderinherit, self).action_confirm()
        configuration = self.env['res.config.settings'].sudo().search([], order="id desc", limit=1)
        if configuration.merge_manufacture_order == True:
            for order in self:
                mrp_production_ids = self.env['mrp.production'].search([('origin', '=', order.name)])
                for mrp_p in mrp_production_ids:
                    mrp_p._onchange_move_raw()
                    mrp_p.write({'state':'draft'})
                    if configuration.by_partner == True:
                        mrp_p.write({"partner_id":order.partner_id.id})
        else:
            for order in self:
                mrp_production_ids = self.env['mrp.production'].search([('origin', '=', order.name)])
                for mrp_p in mrp_production_ids:
                    mrp_p._onchange_move_raw()
                    mrp_p.write({'state':'draft'})
        return result


    @api.depends('procurement_group_id.stock_move_ids.created_production_id.procurement_group_id.mrp_production_ids')
    def _compute_mrp_production_count(self):
        for sale in self:
            sale.mrp_production_count = self.env['mrp.production'].search_count([('origin', 'ilike', sale.name)])

    def action_view_mrp_production(self):
        self.ensure_one()
        mrp_production_ids = self.env['mrp.production'].search([('origin', 'ilike', self.name)])
        action = {
            'res_model': 'mrp.production',
            'type': 'ir.actions.act_window',
        }
        if len(mrp_production_ids.ids) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': mrp_production_ids.ids[0],
            })
        else:
            action.update({
                'name': _("%s Child MO's") % self.name,
                'domain': [('id', 'in', mrp_production_ids.ids)],
                'view_mode': 'tree,form',
            })
        return action



class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    partner_id = fields.Many2one('res.partner','Partner')
    state = fields.Selection(selection_add=[
        ('planned', 'Planned')
    ])

    def unlink(self):
        for production in self:
            if production.state == 'planned' or 'to_close':
                raise UserError(_('Cannot delete a manufacturing order in This State Try to cancel them before'))
        if any(production.state == 'done' for production in self):
            raise UserError(_('Cannot delete a manufacturing order in done state.'))
        self.action_cancel()
        not_cancel = self.filtered(lambda m: m.state != 'cancel')
        if not_cancel:
            productions_name = ', '.join([prod.display_name for prod in not_cancel])
            raise UserError(_('%s cannot be deleted. Try to cancel them before.') % productions_name)

        workorders_to_delete = self.workorder_ids.filtered(lambda wo: wo.state != 'done')
        if workorders_to_delete:
            workorders_to_delete.unlink()
        return super(MrpProduction, self).unlink()


    def duration_day(self):
        configuration = self.env['res.config.settings'].sudo().search([],order="id desc", limit=1)
        if configuration.merge_manufacture_order == True:
            if configuration.by_partner == True:
                if configuration.by_duration in 'day':
                    self.day_cron_job()
                elif configuration.by_duration in 'week':
                    self.weeks_cron_job()
                elif configuration.by_duration in 'month':
                    self.months_cron_job()
            else:
                if configuration.by_duration in 'day':
                    self.day_cron_job()                    
                elif configuration.by_duration in 'week':
                    self.weeks_cron_job()
                elif configuration.by_duration in 'month':
                    self.months_cron_job()

    def day_cron_job(self):
        configuration = self.env['res.config.settings'].sudo().search([],order="id desc", limit=1)
        mo_order_ids = self.env['mrp.production'].search([('state','=','draft')])
        if not mo_order_ids or len(mo_order_ids) == 1:
            return 
        first_mo = mo_order_ids[0]
        product_id = first_mo.product_id.id
        partner_id = first_mo.partner_id.id
        result = [manufacturing_order.id for manufacturing_order in mo_order_ids if manufacturing_order.product_id.id == product_id]
        result2 = [manufacturing_order.id for manufacturing_order in mo_order_ids if manufacturing_order.partner_id.id == partner_id] and [manufacturing_order.id for manufacturing_order in mo_order_ids if manufacturing_order.product_id.id == product_id]
        state_res = [manufacturing_order for manufacturing_order in mo_order_ids if manufacturing_order.state != 'draft']
        if len(result) in [0, 1]:
            raise UserError(
                _('Found Different FG Products !\n\n You can only allow to merge same  product '))
        if len(result) in [0, 1]:
            raise UserError(
                _('Found Different FG customer !\n\n You can only allow to merge same  customer')) 
        if len(state_res):
                raise UserError(
                _('Found Different State !\n\n You can only allow to merge MO with draft status.'))     
        total_qty = 0
        if configuration.merge_manufacture_order == True:
            if configuration.by_partner == True:
                mo_order_result2_ids = self.env['mrp.production'].browse(result2)
                if mo_order_result2_ids:
                    new_mo = mo_order_result2_ids[0].copy()
                    ref = ''
                    for manufacturing_order in mo_order_result2_ids:    
                        total_qty += manufacturing_order.product_qty        
                        if not ref: 
                            ref = manufacturing_order.origin
                        else:
                            ref += ', '+str(manufacturing_order.origin)     
                    new_mo.write({'product_qty':total_qty, 'origin': ref})
                    new_mo._onchange_product_id()
                    new_mo._onchange_move_raw()
                    mo_order_result2_ids.write({'state':'cancel'})
            else:
                mo_order_result_ids = self.env['mrp.production'].browse(result)
                if mo_order_result_ids:
                    new_mo = mo_order_result_ids[0].copy()
                    ref = ''
                    for manufacturing_order in mo_order_result_ids:    
                        total_qty += manufacturing_order.product_qty        
                        if not ref: 
                            ref = manufacturing_order.origin
                        else:
                            ref += ', '+str(manufacturing_order.origin)     
                    new_mo.write({'product_qty':total_qty, 'origin': ref})
                    new_mo._onchange_product_id()
                    new_mo._onchange_move_raw()
                    mo_order_result_ids.write({'state':'cancel'})


    def weeks_cron_job(self):
        configuration = self.env['res.config.settings'].sudo().search([],order="id desc", limit=1)
        mo_order_ids = self.env['mrp.production'].search([('state','=','draft')])
        if not mo_order_ids or len(mo_order_ids) == 1:
            return 
        first_mo = mo_order_ids[0]
        product_id = first_mo.product_id.id
        partner_id = first_mo.partner_id.id
        result = [manufacturing_order.id for manufacturing_order in mo_order_ids if manufacturing_order.product_id.id == product_id]
        result2 = [manufacturing_order.id for manufacturing_order in mo_order_ids if manufacturing_order.partner_id.id == partner_id] and [manufacturing_order.id for manufacturing_order in mo_order_ids if manufacturing_order.product_id.id == product_id]
        state_res = [manufacturing_order for manufacturing_order in mo_order_ids if manufacturing_order.state != 'draft']
        if len(result) in [0, 1]:
            raise UserError(
                _('Found Different FG Products !\n\n You can only allow to merge same  product '))
        if len(result) in [0, 1]:
            raise UserError(
                _('Found Different FG customer !\n\n You can only allow to merge same  customer')) 
        if len(state_res):
                raise UserError(
                _('Found Different State !\n\n You can only allow to merge MO with draft status.'))     
        total_qty = 0
        if configuration.merge_manufacture_order == True:
            if configuration.by_partner == True:
                mo_order_result2_ids = self.env['mrp.production'].browse(result2)
                if mo_order_result2_ids:
                    new_mo = mo_order_result2_ids[0].copy()
                    ref = ''
                    for manufacturing_order in mo_order_result2_ids:    
                        total_qty += manufacturing_order.product_qty        
                        if not ref: 
                            ref = manufacturing_order.origin
                        else:
                            ref += ', '+str(manufacturing_order.origin)     
                    new_mo.write({'product_qty':total_qty, 'origin': ref})
                    new_mo._onchange_product_id()
                    new_mo._onchange_move_raw()
                    mo_order_result2_ids.write({'state':'cancel'})
            else:
                mo_order_result_ids = self.env['mrp.production'].browse(result)
                if mo_order_result_ids:
                    new_mo = mo_order_result_ids[0].copy()
                    ref = ''
                    for manufacturing_order in mo_order_result_ids:    
                        total_qty += manufacturing_order.product_qty        
                        if not ref: 
                            ref = manufacturing_order.origin
                        else:
                            ref += ', '+str(manufacturing_order.origin)     
                    new_mo.write({'product_qty':total_qty, 'origin': ref})
                    new_mo._onchange_product_id()
                    new_mo._onchange_move_raw()
                    mo_order_result_ids.write({'state':'cancel'})


    # @api.multi
    def months_cron_job(self):
        configuration = self.env['res.config.settings'].sudo().search([],order="id desc", limit=1)
        mo_order_ids = self.env['mrp.production'].search([('state','=','draft')])
        if not mo_order_ids or len(mo_order_ids) == 1:
            return 
        first_mo = mo_order_ids[0]
        product_id = first_mo.product_id.id
        partner_id = first_mo.partner_id.id
        result = [manufacturing_order.id for manufacturing_order in mo_order_ids if manufacturing_order.product_id.id == product_id]
        result2 = [manufacturing_order.id for manufacturing_order in mo_order_ids if manufacturing_order.partner_id.id == partner_id] and [manufacturing_order.id for manufacturing_order in mo_order_ids if manufacturing_order.product_id.id == product_id]
        state_res = [manufacturing_order for manufacturing_order in mo_order_ids if manufacturing_order.state != 'draft']
        if len(result) in [0, 1]:
            raise UserError(
                _('Found Different FG Products !\n\n You can only allow to merge same  product '))
        if len(result) in [0, 1]:
            raise UserError(
                _('Found Different FG customer !\n\n You can only allow to merge same  customer')) 
        if len(state_res):
                raise UserError(
                _('Found Different State !\n\n You can only allow to merge MO with draft status.'))     
        total_qty = 0
        if configuration.merge_manufacture_order == True:
            if configuration.by_partner == True:
                mo_order_result2_ids = self.env['mrp.production'].browse(result2)
                if mo_order_result2_ids:
                    new_mo = mo_order_result2_ids[0].copy()
                    ref = ''
                    for manufacturing_order in mo_order_result2_ids:    
                        total_qty += manufacturing_order.product_qty        
                        if not ref: 
                            ref = manufacturing_order.origin
                        else:
                            ref += ', '+str(manufacturing_order.origin)     
                    new_mo.write({'product_qty':total_qty, 'origin': ref})
                    new_mo._onchange_product_id()
                    new_mo._onchange_move_raw()
                    mo_order_result2_ids.write({'state':'cancel'})
            else:
                mo_order_result_ids = self.env['mrp.production'].browse(result)
                if mo_order_result_ids:
                    new_mo = mo_order_result_ids[0].copy()
                    ref = ''
                    for manufacturing_order in mo_order_result_ids:    
                        total_qty += manufacturing_order.product_qty        
                        if not ref: 
                            ref = manufacturing_order.origin
                        else:
                            ref += ', '+str(manufacturing_order.origin)     
                    new_mo.write({'product_qty':total_qty, 'origin': ref})
                    new_mo._onchange_product_id()
                    new_mo._onchange_move_raw()
                    mo_order_result_ids.write({'state':'cancel'})
