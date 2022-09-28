# -*- coding: utf-8 -*-
{
    'name': "Product Packaging",
    'version': '10.0.1.0',
    'summary': """Packages on delivery""",
    'description': """Packages on delivery.""",
    'author': "Rminds Inc.",
    'company': 'Rminds Inc.',
    'website': "https://www.rminds.com",
    'category': 'Inventory',
    'depends': ['base', 'stock'],
    'data': [
        'views/stock_picking.xml',
    ],

    'assets': {
        'web.assets_backend': [
            'rminds_product_packaging/static/src/js/custom_widget.js',
        ],
        'web.assets_frontend': [

        ],

        'web.assets_qweb': [
            'rminds_product_packaging/static/src/xml/custom_widget.xml',
        ],
    },

    'images': ['static/description/icon.png'],
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
}
