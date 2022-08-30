from odoo import fields,api,models

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    qty_copy = fields.Float("qty copy", related="qty_available", store=True)
    reordering_min_qty_copy = fields.Float("Min Qty", related="reordering_min_qty", store=True)
    low_qty_mail_sent = fields.Boolean("Low quantity mail sent",compute='change_mail_sent_status', store=True)
    action_taken = fields.Boolean("Action Taken for low stock")
    stock_low_mail_ids = fields.One2many('stock.low.mail.notify.line', 'product_id')

    @api.depends('qty_available')
    def change_mail_sent_status(self):
        for res in self:
            if res.low_qty_mail_sent and res.qty_available > res.reordering_min_qty:
                res.low_qty_mail_sent = False


    def send_low_stock_via_email(self):
        template_obj = self.env.ref('notify_user_on_low_quantity.mail_template_low_stock_notify')
        products = self.env['product.product'].search([('active', '=', True), ('sale_ok', '=', True), ('default_code', '!=', False)])
        prod_list = []
        stock_low_obj = self.env['stock.low.mail.notify']
        stock_data = False
        valss = {}
        # template_obj.body_html = ""
        for product in products:
            # qty_available = product.qty_copy
            if product.reordering_min_qty and product.qty_available <= product.reordering_min_qty and not product.low_qty_mail_sent:
                vals = {
                    'product_id':product.id,
                    'name': product.name,
                    'qty_available': product.qty_available,
                    'min_qty': product.reordering_min_qty,
                    'low_qty_mail_sent': False,
                }
                product.low_qty_mail_sent = True
                prod_list.append(vals)
                # valss.add(vals)
                # stock_data = stock_low_obj.sudo().create(vals)
        if len(prod_list):
            email = self.env.user.company_id.email
            record = self.env['stock.low.mail.notify'].search([], limit=1)
            new_list = [(5, 0, 0)]
            for product in prod_list:
                new_list.append((0, 0, product))
            if record:
                record.write({'product': new_list})
                template_obj.with_user(2).send_mail(record.id,email_values={'email_to':email},)
            else:
                obj_product = self.env['stock.low.mail.notify'].sudo().create({'name': 'name'})
                obj_product.write({'product': new_list})
                # data = stock_low_obj.search([])
                template_obj.with_user(2).send_mail(obj_product.id,email_values={'email_to': email},)
                # for rec in data:
                #     rec.low_qty_mail_sent = True
        return prod_list 


class MailNotify(models.Model):
    _name = 'stock.low.mail.notify'

    name = fields.Char("")
    product = fields.One2many('stock.low.mail.notify.line','product_ids')


class MailNotifyLine(models.Model):
    _name = 'stock.low.mail.notify.line'

    product_id = fields.Many2one('product.template','product')
    product_ids = fields.Many2one('stock.low.mail.notify')
    name = fields.Char('Product')
    min_qty = fields.Float('Min Quantity')
    qty_available = fields.Float('Quantity Available')
    low_qty_mail_sent = fields.Boolean('Mail Sent')