from odoo import models,api
class ExternalTestingReport(models.AbstractModel):
    _name = 'report.qc_report_templates_rev.report_external_qc_testing'
 


    def append_data(self,data,test_type):
        # import pdb;pdb.set_trace()
        return data.append(test_type)

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['qc.external.testing'].browse(docids)
        # types = [res.test_type.name for res in docs]
        types = []
        type_copy = []
        for line in docs.line_ids:
            types.append(line.test_type.name)
        print('\n\n')
        print(types)
        print('\n\n')

        # import pdb;pdb.set_trace()
        return {
              # 'doc_ids': docids,
              # 'doc_model': model.model,
              'docs': docs,
              'types': types,
              'type_copy': type_copy,
              'append_data': self.append_data,
              # 'issue_date': self.compute_issue_date(docs),
              'rev': self.env['qc.report.template'].search([('product_id','=',docs.product_id.id)]).rev
        }

    # def compute_issue_date(self,docs):
    #   temp_name = self.env['qc.report.template'].search([('product_id','=',docs.product_id.id)])
    #   # import pdb;pdb.set_trace()
    #   return temp_name.create_date

    
