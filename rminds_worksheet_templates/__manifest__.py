# -*- coding: utf-8 -*-

{
    'name': 'Worksheet Templates',
    'category': 'MRP',
    'summary': 'Custom Worksheet Templates',
    'description': """
Custom Worksheet Templates
""",
    'depends': ['quality_control_worksheet'],
    'data': [
        'security/ir.model.access.csv',
        'views/worksheet_templates.xml',
        'views/worksheet_data.xml',
    ],
    'demo': [],
    'assets': {
        'web.assets_backend': [
            'rminds_worksheet_templates/static/src/css/custom.css',
            'rminds_worksheet_templates/static/src/js/pdf_doc.js',
            'rminds_worksheet_templates/static/src/js/relational_fields.js',
        ],
        'web.assets_frontend': [

        ],
    },
}
