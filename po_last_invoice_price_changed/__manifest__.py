{
	"name": "Last invoice Price Changed(PO)",
	"description": "Display last five invoice price for products in purchase order",
	"depends": ['purchase'],
	"data": [
		"views/purchase_views.xml",
		"views/res_config_settings_views.xml"
	],
	"installable": True,
}