from odoo import fields,api,models, _
from odoo.exceptions import UserError

class QCExternalTesting(models.Model):
    _name = 'qc.external.testing'
    _inherit = 'mail.thread'

    mo_id = fields.Many2one('mrp.production', 'Manufacturing Order', track_visibility="always")
    product_id = fields.Many2one("product.product", "Product", required=True, track_visibility="always",store=True)
    line_ids = fields.One2many( 'qc.external.testing.line', 'qc_external_testing_id',"Tests", required=True)
    name = fields.Char("Name", required=True, readonly=True, default='New')
    lab = fields.Many2one("res.users", "Lab User", domain="[('is_lab_user', '=', True)]", required=True,default= lambda self: self.env.user)
    state = fields.Selection([
            ('draft', 'Draft'),
            ('confirm','Confirmed')
        ], default='draft', track_visibility="always")
    attach = fields.Binary("Attachment",)
    customer = fields.Many2one("res.partner","Customer", required=True, track_visibility="always")
    spc = fields.Char("Serving Per Container")
    lot = fields.Char("Lot", required=True, track_visibility="always")
    mfg = fields.Date("MFG", required=True, track_visibility="always")
    # rev = fields.Char("Revision")
    country_id = fields.Many2one("res.country", "Country",default=lambda self: self.env['res.country'].search([('code','=','US')],limit=1), required=True)
    product_size = fields.Char( "Product Size", required=True, track_visibility="always")
    formula = fields.Char("Master Formula", required=True)
    exp_date = fields.Date("Expiry Date", required=True, track_visibility="always")
    fill_date = fields.Date("Fill Date", required=True)
    general_table_ids = fields.One2many('qc.external.general.table','qc_report_template','General Table')
    micro_testing_ids = fields.One2many('qc.external.micro.testing','qc_report_template','MicroBiologicl Testing')
    
    def _get_default_country(self):
        return self.env['res.country'].search([('code', '=', 'US')], limit=1)

    @api.onchange('mo_id')
    def _onchange_mo_id(self):
        if self.mo_id:
            self.product_id = self.mo_id.product_id.id


    def approve_button(self):
        for line in self.line_ids:
            if not line.res:
                raise UserError(_("Result Value not given."))
        self.write({'state': 'confirm'})

    @api.model_create_multi
    def create(self,vals):
        result = super(QCExternalTesting,self).create(vals)
        for res in result:
            if res.name == 'New':
                res.name = self.env['ir.sequence'].next_by_code('qc.external.testing') or 'New'
            if not len(res.line_ids):
                raise UserError(_("Please add atleast One Test Line"))
            if res.exp_date < res.mfg:
                raise UserError(_('You cannot have expiry date before mfg'))
        return result

    @api.depends('mfg,exp_date')
    def validate_exp_date(self):
        # import pdb;pdb.
        if self.exp_date < self.mfg:
            raise UserError(_('You cannot have expiry date before mfg'))

    def write(self,vals):
        result = super(QCExternalTesting,self).write(vals)
        for res in self:
            if not len(res.line_ids):
                raise UserError(_("Please add atleast One Test Line"))
            if res.exp_date < res.mfg:
                raise UserError(_('You cannot have expiry date before mfg'))
        return result

    @api.depends('min_value', 'max_value')
    def change_result(self):
        if self.min_value > 0 or self.max_value > 0:
            if self.res >= self.min_value and self.max_value <= self.max_value:
                self.summary = 'pass'
            else:
                self.summary = 'fail'
        elif self.res == self.spec:
            self.summary = 'pass'
        else: self.summary = 'fail'


    @api.onchange('product_id')
    def onchange_product(self):
        if len(self.line_ids):
            self.line_ids = [(5,0,0)]
        # if len(self.general_table_ids):
        #     self.general_table_ids = [(5,0,0)]
        # if len(self.micro_testing_ids):
        #     self.micro_testing_ids = [(5,0,0)]
        temp_rec = self.env['qc.report.template'].search([('product_id', '=', self.product_id.id)])
        if temp_rec:
            for rec in temp_rec[0].line_ids:
                vals = {'param': rec.param,'min_value': rec.min_value, 'max_value': rec.max_value,'idle': rec.idle, 'unit': rec.unit_id.id,'method': rec.method, 'test_type': rec.test_type.id}
                if rec.min_value > 0:
                    vals.update({'spec': str(rec.min_value) + ' - ' + str(rec.max_value)})
                else:
                    vals.update({'spec': rec.spec})

                self.line_ids = [(0,0,vals)]
            # for rec in temp_rec[0].general_table_ids:
            #     general_vals = {'param': rec.param,'spec': rec.spec}
            #     self.general_table_ids = [(0,0,general_vals)]
            # for rec in temp_rec[0].micro_testing_ids:
            #     micro_vals = {'param': rec.param,'spec': rec.spec,'method': rec.method}
            #     self.write({'micro_testing_ids' : [(0,0,micro_vals)]})



class QCTestLine(models.Model):
    _name = 'qc.external.testing.line'

    param = fields.Many2one("test.attribute","Attribute")
    idle = fields.Char("Target",)
    res = fields.Char("Reported Result")
    min_value = fields.Float("Min Value", )
    max_value = fields.Float("Max Value", )
    method = fields.Char("Method Reference")
    spec = fields.Char("Specification")
    test_type = fields.Many2one("test.type", "Type")
    unit = fields.Many2one('testing.unit')
    # measure = fields.Selection([
    #     ('range','Range'),
    #     ('fixed','Fixed Value')
    #     ],default="fixed")  
    summary = fields.Selection([
        ('pass','Pass'),
        ('fail','Fail')
    ], string="Pass/Fail", compute="change_result")
    qc_external_testing_id = fields.Many2one('qc.external.testing','qc external testing' )

    # @api.onchange('res')
    # def onchange_res(self):
    #     if float(self.res) >= self.min_value and float(self.res) <= self.max_value:
    #         self.write({'summary': 'pass'})
    #     else:
    #         self.write({'summary': 'fail'})
        
    @api.depends('res')
    def change_result(self):
        for record in self:
            if record.min_value > 0 or record.max_value > 0:
                if float(record.res) >= record.min_value and float(record.res) <= record.max_value:
                    record.summary = 'pass'
                else:
                    record.summary = 'fail'
            elif record.res == record.spec:
                record.summary = 'pass'
            else:
                record.summary = 'fail'


class GeneralTable(models.Model):
    _name = 'qc.external.general.table'

    param = fields.Char("Parameter", required=True)
    spec = fields.Char("Specification", required=True)
    result = fields.Char("Result", required=True)
    qc_report_template = fields.Many2one('qc.external.testing','qc external testing' )

class MicroBiologiclTesting(models.Model):
    _name = 'qc.external.micro.testing'

    param = fields.Char("Analytical Parameter", required=True)
    spec = fields.Char("Specification", required=True)
    result = fields.Char("Result", required=True)
    method = fields.Char("Method", required=True)
    date_tested = fields.Date("Date Tested", required=True)
    qc_report_template = fields.Many2one('qc.external.testing','qc report testing' )




