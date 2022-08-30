from odoo import fields, models, api, _

class ResCompany(models.Model):
    _inherit = "res.company"

    overdue_msg = fields.Text(string='Overdue Payments Message', translate=True,
                              default='''Dear Sir/Madam,

    Our records indicate that some payments on your account are still due. Please find details below.
    If the amount has already been paid, please disregard this notice. Otherwise, please forward us the total amount stated below.
    If you have any queries regarding your account, Please contact us.

    Thank you in advance for your cooperation.
    Best Regards,''')