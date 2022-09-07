# -*- coding: utf-8 -*-
{
    'name': 'MO Production Report',
    'category': 'MRP',
    'summary': 'MO Production Report',
    'description': """
MO Production Report'
""",
    'depends': ['rminds_worksheet_templates'],
    'data': [
        'security/ir.model.access.csv',
        'views/worksheet_templates.xml',
        "report/report.xml",
    ],
    'demo': [],
    'assets': {
        'web.assets_backend': [

        ],
        'web.assets_frontend': [

        ],
    },
}
