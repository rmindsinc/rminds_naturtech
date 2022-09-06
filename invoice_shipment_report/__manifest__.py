{
    'name': "Invoice Report Shipment ",
    'version': '15.0.0',
    'summary': """
       """,
    'author': "Rminds INC",
    'website': "http://www.rminds.com",

    'description': """

    """,
    'category': 'account',
    'license': 'LGPL-3',
    # any module necessary for this one to work correctly
    'depends': ['base', 'sale','stock','account','sale_management'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/invoice_shipment.xml',

    ],

}
