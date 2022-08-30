# -*- coding: utf-8 -*-

{
    'name': 'Worksheet Templates',
    'category': 'RMP',
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

        ],
        'web.assets_frontend': [

        ],
    },
}
