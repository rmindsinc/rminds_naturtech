# -*- coding: utf-8 -*-
from ast import literal_eval

from odoo import api, models, fields, _
from odoo.exceptions import UserError


class BOMChecklist(models.Model):
    _name = 'bom.checklist'
    _description = "Define checklist in BOM"

    _order = "x_step,id"

    x_sequence = fields.Integer("Sr. No.")
    x_step = fields.Integer("Step")
    x_name = fields.Text("Instructions")
    x_checklist_id = fields.Many2one('mrp.bom', "BOM")

    # Parameters show flag at backend
    x_start_date_show = fields.Boolean("Start Time")
    x_stop_date_show = fields.Boolean("Stop Time")
    x_ph_show = fields.Boolean("Ph")


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
    _order = "x_step,id"

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

        m2o_field = self.worksheet_template_id.model_id.sudo().model + "_id"
        work_order = self.production_id
        worksheet = self.env[self.worksheet_template_id.model_id.sudo().model].search([('x_quality_check_id', '=', self.id)])
        if not worksheet:
            worksheet = self.env[self.worksheet_template_id.model_id.sudo().model].sudo().create({'x_quality_check_id': self.id})

        if 'mixing_line_ids' in str(worksheet.read()):
            mixing_lines = worksheet.x_mixing_line_ids
            if 'from_manufacturing_order' in self._context and self._context['from_manufacturing_order'] is True:
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
            if 'from_manufacturing_order' in self._context and self._context['from_manufacturing_order'] is True:
                lines_data = []
                if not checklist_lines:
                    for item in work_order.bom_id.x_checklist_ids:
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

        worksheet.x_main_qty = work_order.product_qty

        return super(QualityCheckInherit, self).action_quality_worksheet()