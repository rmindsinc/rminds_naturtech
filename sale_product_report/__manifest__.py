{
    'name': "Sale Product Raw Products ",
    'version': '15.0.0',
    'summary': """
        Product Managment""",
    'author': "Rminds INC",
    'website': "http://www.rminds.com",

    'description': """

    """,
    'category': 'Sale',
    'license': 'LGPL-3',
    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'product','stock','mrp','sale_management'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'report/sale_product_report.xml',

    ],

}
