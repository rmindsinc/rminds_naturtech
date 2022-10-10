# -*- coding: utf-8 -*-
{
	'name' : 'Merge Manufacturing Orders',
	"author": "Edge Technologies",
	'version' : '15.0.1.4',
	'live_test_url':'https://youtu.be/lsusKYoBj9g',
    "images":["static/description/main_screenshot.png"],
	'summary' : 'merge manufacturing merge order merge mrp merge production order merge for manufacturing order merge process combine manufacturing merger manufacturing merge MO merge production merge',
	'description' : """	
			You can merge mrp order Customer wise And  Time duration wise,
			you can merge them By manually and Automatically
	""",
	'depends' : ['stock','sale_management','account','mrp', 'sale_mrp'],
	"license" : "OPL-1",
	'data' : [
		'security/ir.model.access.csv',
		'wizard/merge_manufacturing_order.xml',
		'views/res_config_settings.xml',
		'views/mrp_production_view.xml',
		'data/cron_day.xml',
		'data/cron_week.xml',
		'data/cron_month.xml',
		
	],

	"auto_install": False,
	"installable": True,
	"price": 22,
	"currency": 'EUR',
	'category': 'Sales',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
