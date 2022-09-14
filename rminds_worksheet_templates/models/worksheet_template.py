# -*- coding: utf-8 -*-
from ast import literal_eval
from distutils.command.check import check

from odoo import api, models, fields, _
from odoo.exceptions import UserError
import base64
from PyPDF2 import PdfFileMerger, PdfFileReader


class BOMChecklist(models.Model):
    _name = 'bom.checklist'
    _description = "Define checklist in BOM"

    _order = "x_step,id"

    x_sequence = fields.Integer("Sr. No.")
    x_step = fields.Integer("Step")
    x_name = fields.Text("Instructions")
    x_checklist_id = fields.Many2one('mrp.bom', "BOM")
    x_checklist_id_mo = fields.Many2one('mrp.production', "MO")

    # Parameters show flag at backend
    x_start_date_show = fields.Boolean("Start Time")
    x_stop_date_show = fields.Boolean("Stop Time")
    x_ph_show = fields.Boolean("Ph")
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")
    name = fields.Char("Name")


class BOMChecklist(models.Model):
    _name = 'mo.checklist'
    _description = "Checklist in MO"

    _order = "x_sequence,id"

    x_sequence = fields.Integer("Sr. No.")
    x_step = fields.Integer("Step")
    x_name = fields.Text("Instructions")
    x_checklist_id = fields.Many2one('mrp.bom', "BOM")
    x_checklist_id_mo = fields.Many2one('mrp.production', "MO")

    # Parameters show flag at backend
    x_start_date_show = fields.Boolean("Start Time")
    x_stop_date_show = fields.Boolean("Stop Time")
    x_ph_show = fields.Boolean("Ph")

    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")
    name = fields.Char("Name")


class MRPBOM(models.Model):
    _inherit = 'mrp.bom'

    x_checklist_ids = fields.One2many('bom.checklist', 'x_checklist_id', "Checklist")
    x_revision_memo = fields.Text("BOM revision history")


class WorksheetTemplate(models.Model):
    _inherit = 'worksheet.template'
    _description = "For which kind of process this template will be used (Mixing, Filling, Packaging etc.)"

    x_template_for = fields.Selection([('mixing', 'Mixing'), ('filling', 'Filling'), ('packing', 'Packaging')])


class WorksheetChecklist(models.Model):
    _name = 'worksheet.checklist'
    _description = "Checklist to show in worksheet"
    _order = "x_sequence,id"

    x_sequence = fields.Integer("Sr. No.")
    x_step = fields.Integer("Step")
    x_name = fields.Text("Instructions")
    x_completed_by = fields.Many2one('res.users', "Completed by")
    x_completed_date = fields.Date("Date")
    x_verified_by = fields.Many2one('res.users', "Verified by")
    x_verified_date = fields.Date("Date")

    # Parameters
    x_start_date = fields.Datetime("Start Time")
    x_stop_date = fields.Datetime("Stop Time")
    x_ph = fields.Float("Ph")

    # Parameters show flag
    x_start_date_show = fields.Boolean("Start Time")
    x_stop_date_show = fields.Boolean("Stop Time")
    x_ph_show = fields.Boolean("Ph")


class MixingLines(models.Model):
    _name = 'mixing.lines'
    _description = "BOM Lines to show in worksheet"

    x_part = fields.Char("Part")
    x_product_id = fields.Many2one('product.product', "Description")
    x_qty = fields.Float("Quantity")
    x_uom = fields.Many2one('uom.uom', "Unit")
    x_added_by = fields.Many2one("res.users", "Added by")
    x_verify_by = fields.Many2one("res.users", "Verified by")
    x_qc_name = fields.Char("QC name")


class IrModels(models.Model):

    _inherit = 'ir.model'

    @api.model
    def create(self, vals):
        """
        When we click on DESIGN TEMPLATE it creates new object/model
        we need to create all required fields into newly created model according to template type(Template for)
        so that these fields will be available in drag-drop screen while designing.
        :param vals:
        :return:
        """

        res = super(IrModels, self).create(vals)
        current_worksheet_template = self.env['worksheet.template'].search([('name', '=', vals['name'])])

        if 'model' in vals and 'x_quality_check_worksheet_template' in vals['model']:
            if current_worksheet_template.x_template_for == 'mixing':
                new_fields = [
                    ['x_main_qty', 'float', 'Quantity'],
                    ['x_main_unit', 'many2one', 'Unit', 'uom.uom'],

                    ['x_manufactured_date', 'datetime', 'Manufactured Date'],
                    ['x_total_weight', 'float', 'Total Weight'],

                    ['x_start_time', 'datetime', 'Start time'],
                    ['x_stop_time', 'datetime', 'Stop time'],
                    ['x_retain', 'char', 'Retain'],
                    ['x_tank_used', 'char', 'Tank used'],
                    ['x_scale_used', 'char', 'Scale used'],
                ]
                for item in new_fields:
                    if item[1] == 'many2one':
                        self.env['ir.model.fields'].create({
                            'name': item[0],
                            'model_id': self.env['ir.model'].search([('model', '=', vals['model'])]).id,
                            'field_description': item[2],
                            'ttype': item[1],
                            'store': True,
                            'relation': item[3],
                        })
                    else:
                        self.env['ir.model.fields'].create({
                            'name': item[0],
                            'model_id': self.env['ir.model'].search([('model', '=', vals['model'])]).id,
                            'field_description': item[2],
                            'ttype': item[1],
                            'store': True,
                        })

                # Create mixing lines O2M field === start ===
                self.env['ir.model.fields'].create({
                    'name': 'x_'+vals['model']+"_id",
                    'ttype': 'many2one',
                    'relation': vals['model'],
                    'field_description': _('Template worksheet'),
                    'model_id': self.env['ir.model'].search([('model', '=', 'mixing.lines')]).id,
                })
                self.env['ir.model.fields'].create({
                    'model_id': self.env['ir.model'].search([('model', '=', vals['model'])]).id,
                    'name': 'x_mixing_line_ids',
                    'ttype': 'one2many',
                    'relation': 'mixing.lines',
                    'relation_field': 'x_'+vals['model']+"_id",
                    'field_description': "BOM Lines",
                })
                # === end ===

                # Create checklist/instructions lines O2M field === start ===
                self.env['ir.model.fields'].create({
                    'name': 'x_'+vals['model'] + "_id",
                    'ttype': 'many2one',
                    'relation': vals['model'],
                    'field_description': _('Template worksheet'),
                    'model_id': self.env['ir.model'].search([('model', '=', 'worksheet.checklist')]).id,
                })
                self.env['ir.model.fields'].create({
                    'model_id': self.env['ir.model'].search([('model', '=', vals['model'])]).id,
                    'name': 'x_checklist_line_ids',
                    'field_description': 'Checklist/Instructions',
                    'ttype': 'one2many',
                    'relation': 'worksheet.checklist',
                    'relation_field': 'x_'+vals['model'] + "_id",
                })
                # === end ===

        return res


class QualityCheckInherit(models.Model):

    _inherit = 'quality.check'

    def action_quality_worksheet(self):
        """
        Method overridden to fill worksheet with some default values(like BOM lines, instructions etc.)
        :return:
        """

        if self.worksheet_template_id:
            m2o_field = self.worksheet_template_id.model_id.sudo().model + "_id"
            work_order = self.production_id
            worksheet = self.env[self.worksheet_template_id.model_id.sudo().model].search([('x_quality_check_id', '=', self.id)])
            if not worksheet:
                worksheet = self.env[self.worksheet_template_id.model_id.sudo().model].sudo().create({'x_quality_check_id': self.id})

            exist = work_order.related_captured_templates or ''
            work_order.related_captured_templates = exist + '@@' + self.worksheet_template_id.model_id.sudo().model + '##' + str(worksheet.id) + "##" + self.worksheet_template_id.x_template_for

            if 'mixing_line_ids' in str(worksheet.read()):
                mixing_lines = worksheet.x_mixing_line_ids
                if 1==1 or 'from_manufacturing_order' in self._context and self._context['from_manufacturing_order'] is True:
                    lines_data = []
                    if not mixing_lines:
                        for item in work_order.move_raw_ids:
                            lines_data.append((0, 0, {
                                'x_product_id': item.product_id.id,
                                'x_part': item.product_id.default_code or '',
                                'x_qty': item.product_uom_qty,
                                'x_uom': item.product_id.product_tmpl_id.uom_id.id,
                                'x_added_by': False,
                                'x_verify_by': False,
                                'x_qc_name': worksheet.x_name,
                                'x_'+m2o_field: worksheet.sudo().id,
                            }))
                        if lines_data: worksheet.x_mixing_line_ids = lines_data

            if 'checklist_line_ids' in str(worksheet.read()):
                checklist_lines = worksheet.x_checklist_line_ids
                added_steps = []
                items_to_delete = []
                for exist_item in worksheet.x_checklist_line_ids:
                    added_steps.append(exist_item.x_step)
                    if exist_item.x_step == 98765:
                        items_to_delete.append(exist_item)
                for item in items_to_delete:
                    item.unlink()

                if 1==1 or 'from_manufacturing_order' in self._context and self._context['from_manufacturing_order'] is True:
                    if 1 == 1 or not checklist_lines:
                        for item in work_order.x_checklist_ids_mo:
                            print (item.x_name, item.display_type, "ITEM =============================")
                            lines_data = []
                            if item.x_step not in added_steps:
                                if item.display_type and item.display_type == 'line_section':
                                    data = {
                                        'x_name': item.name,
                                        'x_' + m2o_field: worksheet.sudo().id,
                                        'x_sequence': item.x_sequence,
                                        'x_step': 98765,
                                    }
                                else:
                                    data = {
                                        'x_name': item.x_name,
                                        'x_'+m2o_field: worksheet.sudo().id,
                                        'x_sequence': item.x_sequence,
                                        'x_step': item.x_step,
                                    }
                                # Show only marked fields to fill
                                if item.x_start_date_show: data.update({'x_start_date_show': True})
                                if item.x_stop_date_show: data.update({'x_stop_date_show': True})
                                if item.x_ph_show: data.update({'x_ph_show': True})

                                lines_data.append((0, 0, data))
                                if lines_data: worksheet.x_checklist_line_ids = lines_data

            try:
                worksheet.x_main_qty = work_order.product_qty
            except Exception as e: pass

        return super(QualityCheckInherit, self).action_quality_worksheet()


class MRPProduction(models.Model):
    _inherit = 'mrp.production'

    x_checklist_ids_mo = fields.One2many('mo.checklist', 'x_checklist_id_mo', "Checklist")
    x_revision_memo_mo = fields.Text("BOM revision history")

    related_captured_templates = fields.Char("Related captured worksheet templates")

    @api.onchange('bom_id')
    def _onchange_bom_id(self):
        res = super(MRPProduction, self)._onchange_bom_id()
        for ch in self:
            ch.x_checklist_ids_mo = [(5,0,0)]
        if self.bom_id:
            ch_ids = []
            for item in self.bom_id.x_checklist_ids:
                checklist_data = {
                    'x_step': item.x_step,
                    'x_name': item.x_name,
                    'x_sequence': item.x_sequence,
                    'display_type': item.display_type,
                    'name': item.name,
                }
                ch_id = self.env['mo.checklist'].create(checklist_data)
                ch_ids.append(ch_id.id)
            self.x_checklist_ids_mo = [(6, 0, ch_ids)]
            self.x_revision_memo_mo = self.bom_id.x_revision_memo
            #self.is_percentage = self.bom_id.is_percentage
        return res

    def action_confirm(self):
        res = super(MRPProduction, self).action_confirm()
        quality_checks = self.env['quality.check'].sudo().search([('production_id', '=', self.id)])
        for quality_check in quality_checks:
            try:
                quality_check.action_quality_worksheet()
            except Exception as e:
                pass

        for mo in self:
            for ch in mo:
                ch.x_checklist_ids_mo = [(5, 0, 0)]
            if mo.bom_id:
                ch_ids = []
                for item in mo.bom_id.x_checklist_ids:
                    checklist_data = {
                        'x_step': item.x_step,
                        'x_name': item.x_name,
                        'x_sequence': item.x_sequence,
                        'display_type': item.display_type,
                        'name': item.name,
                    }
                    ch_id = self.env['mo.checklist'].create(checklist_data)
                    ch_ids.append(ch_id.id)
                mo.x_checklist_ids_mo = [(6, 0, ch_ids)]
                mo.x_revision_memo_mo = mo.bom_id.x_revision_memo

            for sm in mo.move_raw_ids:
                for bom_item in mo.bom_id.bom_line_ids:
                    if sm.product_id.id == bom_item.product_id.id:
                        sm.mo_percentage = bom_item.bom_percentage

        return res

    def _generate_backorder_productions(self, close_mo=True):
        backorders = super(MRPProduction, self)._generate_backorder_productions(close_mo)
        for mo in backorders:
            new_ids = [item.copy().id for item in self.x_checklist_ids_mo]
            mo.x_checklist_ids_mo = new_ids
            mo.x_revision_memo_mo = self.x_revision_memo_mo
        return backorders


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm123(self):
        res = super(SaleOrder, self).action_confirm()
        for mo in self.env['mrp.production'].sudo().search([('origin', '=', self.name)]):
            for ch in mo:
                ch.x_checklist_ids_mo = [(5, 0, 0)]
            if mo.bom_id:
                ch_ids = []
                for item in mo.bom_id.x_checklist_ids:
                    checklist_data = {
                        'x_step': item.x_step,
                        'x_name': item.x_name,
                        'x_sequence': item.x_sequence,
                        'display_type': item.display_type,
                        'name': item.name,
                    }
                    ch_id = self.env['mo.checklist'].create(checklist_data)
                    ch_ids.append(ch_id.id)
                mo.x_checklist_ids_mo = [(6, 0, ch_ids)]
                mo.x_revision_memo_mo = mo.bom_id.x_revision_memo

            # for child MO
            chlid_mo = mo.procurement_group_id.stock_move_ids.created_production_id.procurement_group_id.mrp_production_ids - mo
            for child in chlid_mo:
                for ch in child:
                    ch.x_checklist_ids_mo = [(5, 0, 0)]
                if child.bom_id:
                    ch_ids = []
                    for item in child.bom_id.x_checklist_ids:
                        checklist_data = {
                            'x_step': item.x_step,
                            'x_name': item.x_name,
                            'x_sequence': item.x_sequence,
                            'display_type': item.display_type,
                            'name': item.name,
                        }
                        ch_id = self.env['mo.checklist'].create(checklist_data)
                        ch_ids.append(ch_id.id)
                    child.x_checklist_ids_mo = [(6, 0, ch_ids)]
                    child.x_revision_memo_mo = child.bom_id.x_revision_memo

            for sm in mo.move_raw_ids:
                for bom_item in mo.bom_id.bom_line_ids:
                    if sm.product_id.id == bom_item.product_id.id:
                        sm.mo_percentage = bom_item.bom_percentage

            for sm in chlid_mo.move_raw_ids:
                for bom_item in chlid_mo.bom_id.bom_line_ids:
                    if sm.product_id.id == bom_item.product_id.id:
                        sm.mo_percentage = bom_item.bom_percentage

        return res
