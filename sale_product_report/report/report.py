from odoo import models,api,fields



class SaleProductReport(models.AbstractModel):
    _name = 'report.sale_product_report.sale_product_report'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['sale.order'].browse(docids)
        manu_route_id = self.env['stock.location.route'].search([('name',"=","Manufacture")])
        sale_line_data = []
        for line in docs.order_line:

            if manu_route_id in line.product_id.route_ids:
                pass

            else:
                sale_line_data.append(line)


        mo_objs = docs.procurement_group_id.stock_move_ids.created_production_id

        list_data = []
        for mo in mo_objs:
            list_data.append(mo.id)
        def tri_recursion(mo_objs_var):
            if mo_objs_var:
                child_mos = (mo_objs_var.procurement_group_id.stock_move_ids.created_production_id.procurement_group_id.mrp_production_ids)
                if len(child_mos)>1:
                    for child_mo in child_mos:

                        list_data.append(child_mo.id)
                else:

                    r_data = (mo_objs_var.procurement_group_id.stock_move_ids.created_production_id.procurement_group_id.mrp_production_ids.id)
                    if r_data:
                        list_data.append(r_data)
                result =tri_recursion(mo_objs_var.procurement_group_id.stock_move_ids.created_production_id.procurement_group_id.mrp_production_ids)

            else:
                result = 0
            return result


        for mo_objs_var in mo_objs:
            tri_recursion(mo_objs_var)

        mo_objs1 = self.env['mrp.production'].sudo().search([("id","in",list_data),["state","!=","cancel"]])
        mo_data = {}
        raws = mo_objs1.mapped('move_raw_ids').sorted(
            key=lambda r: r.product_id.id)
        for r in raws:
            key = (r.product_id.id)
            if key not in mo_data:
                mo_data[key] = {
                    'product_id': r.product_id.display_name,
                    'total_qty': r.product_uom_qty,
                    'unit': r.product_uom.name,
                    'origin': r.reference,

                }
            else:
                mo_data[key].update({
                    'total_qty': mo_data[key].get('total_qty') + r.product_uom_qty,
                    'origin': mo_data[key].get('origin')+', '+r.reference,
                })


        return {
            'doc_ids': docids,
            'doc_model':'sale.order',
            'docs': docs,
            # 'purchase':po_line_attribute_objs,
            'sale':sale_line_data,
            'consume':mo_data,
            'data': data,
        }