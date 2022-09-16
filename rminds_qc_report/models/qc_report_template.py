from odoo import fields,api,models, _
from odoo.exceptions import UserError

class QCReportTemplate(models.Model):
    _name = 'qc.report.template'

    product_id = fields.Many2many("product.product", required=True)
    line_ids = fields.One2many( 'qc.test.line', 'qc_report_template',"Physcial & Chemical Section", required=True)
    name = fields.Char("Name", required=True)
    # general_table_ids = fields.One2many('qc.general.table','qc_report_template','Visual Test Section')
    # micro_testing_ids = fields.One2many('qc.micro.testing','qc_report_template','General Table')
    rev = fields.Char('revision', readonly=True, default="Original")
    def _add_domain(self):
        table_obj = self.env['general.table'].search([('product_id','=',self.product_id.id)])  
        if table_obj:
            domain = [('id', 'in', table_obj.ids)]
        else:
            domain = [('id', '=', -1)]
        return domain
    gen_table_ids = fields.Many2many('qc.general.table')
    # physical_ids = fields.Many2many('phyical.checmical.table')
    # micro_ids = fields.Many2many('micro.table')

    _sql_constraints = [('unique_product__id', 'unique (product_id)',
                         'This product has already assigned to one record')]


    @api.model_create_multi
    def create(self,vals):
        result = super(QCReportTemplate,self).create(vals)
        for res in result:
            if not len(res.line_ids):
                raise UserError(_("Please add atleast One Test Line"))
        return result

    def write(self,vals):
        vals.update({ 'rev' : self.env['ir.sequence'].next_by_code('qc.report.template')}) 
        result = super(QCReportTemplate,self).write(vals)
        for res in self:
            if not len(res.line_ids):
                raise UserError(_("Please add atleast One Test Line"))
        return result


    @api.onchange('gen_table_ids')
    def onchange_gen_ids(self):
        for res in self:
            res.line_ids = [(5,0,0)]
        for lines in self.gen_table_ids:
            for line in lines.line_ids:
                vals = {'param': line.param.id,'min_value':line.min_value,'max_value': line.max_value,'unit_id': line.unit_id.id, 'method': line.method,'spec': line.spec, 'test_type': line.test_type.id,'target': line.target}
                if line.min_value > 0:
                    vals.update({'spec': str(line.min_value) + ' - ' + str(line.max_value)})
                else:
                    vals.update({'spec': line.spec})
                general_id = self.env['qc.test.line'].create(vals)
                self.line_ids =   [(4,general_id.id)]

    @api.onchange('physical_ids')
    def onchange_physical_ids(self):
        for res in self:
            res.line_ids = [(5,0,0)]
        for lines in self.physical_ids:
            for line in lines.line_ids:
                vals = {'param': line.param,'min_value':line.min_value,'max_value': line.max_value,'idle':line.idle,'unit': line.unit_id.name}
                general_id = self.env['qc.test.line'].create(vals)
                self.line_ids =  [(4,general_id.id)]

    @api.onchange('micro_ids')
    def onchange_micro_ids(self):
        for res in self:
            res.micro_testing_ids = [(5,0,0)]
        for lines in self.micro_ids:
            for line in lines.line_ids:
                vals = {'param': line.param,'spec':line.spec,'method': line.method}
                general_id = self.env['qc.micro.testing'].create(vals)
                self.micro_testing_ids =  [(4,general_id.id)]



class QCTestLine(models.Model):
    _name = 'qc.test.line'

    param = fields.Many2one("test.attribute","Attribute", required=True)
    idle = fields.Char("Target")
    target = fields.Char("Target")
    min_value = fields.Float("Min Value")
    method = fields.Char("Method Reference")
    test_type = fields.Many2one("test.type", "Type")
    spec = fields.Char("Specification")
    unit_id = fields.Many2one('testing.unit', 'Testing Unit')
    max_value = fields.Float("Max Value")
    qc_report_template = fields.Many2one('qc.report.template','qc report template' )



class GeneralTable(models.Model):
    _name = 'qc.general.table'

    name = fields.Char("Name")
    product_id = fields.Many2many("product.product", required=True)
    line_ids = fields.One2many('qc.general.table.line','general_table_id','Lines' )

    @api.model_create_multi
    def create(self,vals):
        result = super(GeneralTable,self).create(vals)
        for res in result:
            if not res.name:
                raise UserError(_('Please add a name to record'))
            if not len(res.line_ids):
                raise UserError(_("Please add atleast One Test Line"))
        return result

    def write(self,vals):
        result = super(GeneralTable,self).write(vals)
        for res in self:
            if not len(res.line_ids):
                raise UserError(_("Please add atleast One Test Line"))
        return result


class GeneralTableLine(models.Model):
    _name = 'qc.general.table.line'

    param = fields.Many2one("test.attribute","Attribute", required=True)
    method = fields.Char("Method Reference",)
    min_value = fields.Float("Min Value")
    max_value = fields.Float("Max Value")
    test_type = fields.Many2one("test.type", "Type", required=True)
    spec = fields.Char("Specification")
    unit_id = fields.Many2one('testing.unit', 'Testing Unit')
    target = fields.Char("Target")
    actual_result = fields.Char("Actual Result")
    general_table_id = fields.Many2one('qc.general.table','general table id' )
    test = fields.Char("test")

    method_1 = fields.Boolean("Method Reference",compute='_field_compute')
    spec_1 = fields.Boolean("Specification",compute='_field_compute')
    # res = fields.Boolean("Result")
    min_value_1 = fields.Boolean("Min Value",compute='_field_compute')
    max_value_1 = fields.Boolean("Max Value",compute='_field_compute')
    target_1 = fields.Boolean("Target",compute='_field_compute')
    # date_tested = fields.Boolean("Date Tested")
    unit_id_1 = fields.Boolean('Testing Unit',compute='_field_compute')

    @api.depends('test_type')
    def _field_compute(self):
        for rec in self:
            if rec.test_type:
                if rec.test_type.name:
                    rec.method_1 = rec.test_type.method
                    rec.spec_1 = rec.test_type.spec
                    rec.min_value_1 = rec.test_type.min_value
                    rec.max_value_1 = rec.test_type.max_value
                    rec.target_1 = rec.test_type.target
                    rec.unit_id_1 = rec.test_type.unit_id






class MRPBOM(models.Model):
    _inherit = 'mrp.bom'

    x_test_id = fields.Many2one('qc.general.table', string="COA Test")


# class GeneralTable(models.Model):
#     _name = 'general.table'

#     name = fields.Char("Name", required=True)
#     # product_id = fields.Many2one("product.product", required=True)
#     line_ids = fields.One2many('general.table.line','generl_table_id','Lines')

#     @api.model_create_multi
#     def create(self,vals):
#         result = super(GeneralTable,self).create(vals)
#         for res in result:
#             if not len(res.line_ids):
#                 raise UserError(_("Please add atleast One Test Line"))
#         return result

#     def write(self,vals):
#         result = super(GeneralTable, self).write(vals)
#         for record in self:
#             if not len(record.line_ids):
#                 raise UserError(_("Please add atleast One Test Line"))
#         return result

# class GeneralTableLine(models.Model):
#     _name = 'general.table.line'

#     param = fields.Char("Parameter", required=True)
#     spec = fields.Char("Specification", required=True)
#     generl_table_id = fields.Many2one('general.table','general table' ) 


# class PhysicalTable(models.Model):
#     _name = 'phyical.checmical.table'

#     name = fields.Char("Name", required=True)
#     # product_id = fields.Many2one("product.product", required=True)
#     line_ids = fields.One2many('phyical.checmical.table.line','physical_table_id','Lines')

#     @api.model_create_multi
#     def create(self,vals):
#         result = super(PhysicalTable,self).create(vals)
#         for res in result:
#             if not len(res.line_ids):
#                 raise UserError(_("Please add atleast One Test Line"))
#         return result

#     def write(self,vals):
#         result = super(PhysicalTable, self).write(vals)
#         for record in self:
#             if not len(record.line_ids):
#                 raise UserError(_("Please add atleast One Test Line"))
#         return result



# class PhysicalTableLine(models.Model):
#     _name = 'phyical.checmical.table.line'

#     param = fields.Char("Physcial & Chemical", required=True)
#     idle = fields.Char("Target")
#     # unit = fields.Char("Unit")
#     min_value = fields.Float("Minimum")
#     unit_id = fields.Many2one('testing.unit',"Unit")
#     # measure = fields.Selection([
#     #     ('range','Range'),
#     #     ('fixed','Fixed Value')
#     #     ],default="fixed")  
#     max_value = fields.Float("Maximum")
#     physical_table_id = fields.Many2one('phyical.checmical.table','phyical checmical table' ) 

#     # @api.onchange('measure')
#     # def onchange_measure(self):
#     #     # for res in self:
#     #     if self.measure == 'fixed':
#     #         self.min_value = self.max_value = 0.0
#     #     else:
#     #         self.idle = ''


# class MicroTable(models.Model):
#     _name = 'micro.table'

#     name = fields.Char("Name",required=True)
#     # product_id = fields.Many2one("product.product", required=True)
#     line_ids = fields.One2many('micro.table.line','micro_table_id','Lines')

#     @api.model_create_multi
#     def create(self,vals):
#         result = super(MicroTable,self).create(vals)
#         for res in result:
#             if not len(res.line_ids):
#                 raise UserError(_("Please add atleast One Test Line"))
#         return result

#     def write(self,vals):
#         result = super(MicroTable, self).write(vals)
#         for record in self:
#             if not len(record.line_ids):
#                 raise UserError(_("Please add atleast One Test Line"))
#         return result

# class MicroTableLine(models.Model):
#     _name = 'micro.table.line'

#     param = fields.Char("Analytical Parameter", required=True)
#     spec = fields.Char("Specification", required=True)
#     method = fields.Char("Method", required=True)
#     micro_table_id = fields.Many2one('micro.table','micro table' )


class MicroTableLine(models.Model):
    _name = 'testing.unit'

    name = fields.Char("Name", required=True)

class TestAttributes(models.Model):
    _name = 'test.attribute'

    name = fields.Char("Name")

class TestType(models.Model):
    _name = 'test.type'



    def _default_sequence(self):
        cat = self.search([], limit=1, order="sequence DESC")
        if cat:
            return cat.sequence + 1
        return 100

    name = fields.Char("Name")
    sequence = fields.Integer("Sequence",required=True,default=_default_sequence)
    # param = fields.Boolean("Attribute")
    method = fields.Boolean("Method Reference")
    spec = fields.Boolean("Specification")
    res = fields.Boolean("Result")
    min_value = fields.Boolean("Min Value")
    max_value = fields.Boolean("Max Value")
    target = fields.Boolean("Target")
    date_tested = fields.Boolean("Date Tested")
    unit_id = fields.Boolean('Testing Unit')

    _sql_constraints = [
        ('sequence', 'unique(sequence)', "Another Test already exists with this sequence number!"),
    ]

    # param = fields.Many2one("test.attribute", "Attribute", required=True)
    # method = fields.Char("Method Reference", )
    # min_value = fields.Float("Min Value")
    # max_value = fields.Float("Max Value")
    # test_type = fields.Many2one("test.type", "Type")
    # spec = fields.Char("Specification", required=True)
    # unit_id = fields.Many2one('testing.unit', 'Testing Unit')
    # target = fields.Char("Target")
    # general_table_id = fields.Many2one('qc.general.table', 'general table id')
