{
	"name": "Notify User for Low Inventory",
	"depends": ['product','stock'],
	"data": [
		"security/ir.model.access.csv",
		"views/ir_cron.xml",
		"views/product_views.xml",
		"views/email_templates.xml",
	],
	"installable": True,
}