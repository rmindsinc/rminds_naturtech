from odoo import models,api, fields
import base64
from PyPDF2 import PdfFileMerger, PdfFileReader


class MRPProduction(models.Model):
    _inherit = 'mrp.production'

    def has_qc_check(self):
        if self.env['qc.external.testing'].search([('mo_id', '=', self.id)]):
            return True
        else:
            False

    def get_qc_check(self):
        return self.env['qc.external.testing'].search([('mo_id', '=', self.id)], limit=1)

    def generate_production_report(self):
        report_file = "/tmp/worksheet%s.pdf" % self.id
        files = [report_file]
        paper_format = self.env['report.paperformat'].sudo().search([('name', 'ilike', 'US Letter')], limit=1)
        if paper_format:
            exist_margin_top = paper_format.margin_top
            exist_header_spacing = paper_format.header_spacing
            paper_format.margin_top = 60
            paper_format.header_spacing = 55
        report = self.env.ref('rminds_production_report.action_report_production_report')._render_qweb_pdf(self.id)
        f = open(report_file, 'wb+')
        f.write(report[0])
        f.close()
        if paper_format:
            paper_format.margin_top = exist_margin_top
            paper_format.header_spacing = exist_header_spacing

        for bom_line in self.bom_id.bom_line_ids:
            domain = [
                '|',
                '&', ('res_model', '=', 'product.product'), ('res_id', '=', bom_line.product_id.id),
                '&', ('res_model', '=', 'product.template'), ('res_id', '=', bom_line.product_id.product_tmpl_id.id)]
            attachment_ids = self.env['mrp.document'].sudo().search(domain)
            for attachment in attachment_ids:
                file_name = "/tmp/bom_line%s.pdf" % attachment.id
                f = open(file_name, 'wb+')
                files.append(file_name)
                f.write(base64.decodebytes(attachment.datas))
                f.close()

        merger = PdfFileMerger()
        for pdf_file in files:
            merger.append(PdfFileReader(pdf_file, 'rb'), import_bookmarks=False)
        final_file = "/tmp/merged_2_pages%s.pdf" % self.id
        f2 = open(final_file, 'wb+')
        f2.close()
        merger.write(final_file)
        merger.close()

        f2 = open(final_file, 'rb')
        final_pdf_file = self.env['ir.attachment'].create({
            'name': 'Mixing Workorder Report - %s' % self.name,
            'datas': base64.b64encode(f2.read()),
            'res_model': 'mrp.production',
            'res_id': self.id,
            'mimetype': 'application/pdf'
        })

        action = {
            'type': 'ir.actions.act_url',
            'url': "web/content/?model=ir.attachment&id=" + str(
                final_pdf_file.id) + "&filename_field=name&field=datas&download=true&name=" + final_pdf_file.name,
            'target': 'self'
        }
        return action

    def generate_production_workorder_report(self):
        # verify first template is created
        quality_checks = self.env['quality.check'].sudo().search([('production_id', '=', self.id)])
        for quality_check in quality_checks:
            try:
                quality_check.action_quality_worksheet()
            except Exception as e:
                pass

        paper_format = self.env['report.paperformat'].sudo().search([('name', 'ilike', 'US Letter')], limit=1)
        if paper_format:
            exist_margin_top = paper_format.margin_top
            exist_header_spacing = paper_format.header_spacing
            paper_format.margin_top = 60
            paper_format.header_spacing = 55

        report_file = "/tmp/worksheet%s.pdf" % self.id
        files = [report_file]
        report = self.env.ref('rminds_production_report.action_report_production_workorder_report')._render_qweb_pdf(self.id)

        f = open(report_file, 'wb+')
        f.write(report[0])
        f.close()

        if paper_format:
            paper_format.margin_top = exist_margin_top
            paper_format.header_spacing = exist_header_spacing

        for bom_line in self.bom_id.bom_line_ids:
            domain = [
                '|',
                '&', ('res_model', '=', 'product.product'), ('res_id', '=', bom_line.product_id.id),
                '&', ('res_model', '=', 'product.template'), ('res_id', '=', bom_line.product_id.product_tmpl_id.id)]
            attachment_ids = self.env['mrp.document'].sudo().search(domain)
            for attachment in attachment_ids:
                file_name = "/tmp/bom_line%s.pdf" % attachment.id
                f = open(file_name, 'wb+')
                files.append(file_name)
                f.write(base64.decodebytes(attachment.datas))
                f.close()

        merger = PdfFileMerger()
        for pdf_file in files:
            merger.append(PdfFileReader(pdf_file, 'rb'), import_bookmarks=False)
        final_file = "/tmp/merged_2_pages%s.pdf" % self.id
        f2 = open(final_file, 'wb+')
        f2.close()
        merger.write(final_file)
        merger.close()

        f2 = open(final_file, 'rb')
        final_pdf_file = self.env['ir.attachment'].create({
            'name': 'Production Workorder Report - %s' % self.name,
            'datas': base64.b64encode(f2.read()),
            'res_model': 'mrp.production',
            'res_id': self.id,
            'mimetype': 'application/pdf'
        })

        action = {
            'type': 'ir.actions.act_url',
            'url': "web/content/?model=ir.attachment&id=" + str(
                final_pdf_file.id) + "&filename_field=name&field=datas&download=true&name=" + final_pdf_file.name,
            'target': 'self'
        }
        return action

    def get_percentage(self, product_id):
        percentage = 0
        for item in self.move_raw_ids:
            if item.product_id.id == product_id.id:
                percentage = item.mo_percentage * 100
                percentage = format(percentage, '.4f')
        if not percentage:
            percentage = ''
        return percentage

    def get_customer(self):
        customer = ""
        if self.origin:
            so = self.env['sale.order'].search([('name', '=', self.origin)])
            if so:
                customer = so.partner_id.name
            if not so:
                mo = self.env['mrp.production'].search([('name', '=', self.origin)])
                if mo:
                    so = self.env['sale.order'].search([('name', '=', mo.origin)])
                    if so:
                        customer = so.partner_id.name
        return customer

    def get_customer_ref(self):
        customer_ref = ""
        if self.origin:
            so = self.env['sale.order'].search([('name', '=', self.origin)])
            if so:
                customer_ref = so.partner_id.name
            if not so:
                mo = self.env['mrp.production'].search([('name', '=', self.origin)])
                if mo:
                    so = self.env['sale.order'].search([('name', '=', mo.origin)])
                    if so:
                        customer_ref = so.partner_id.name
        return customer_ref


class StockMove(models.Model):
    _inherit = 'stock.move'

    def get_lots(self):
        lots = []
        for ml in self.move_line_ids:
            if ml.lot_id:
                lots.append(ml.lot_id.name)
        return ",".join(lots)