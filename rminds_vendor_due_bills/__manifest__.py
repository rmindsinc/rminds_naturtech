{
	"name": "Notify User for Due Vendor Bills",
	"depends": ['account'],
	"data": [
		"security/ir.model.access.csv",
		"views/ir_cron.xml",
		"views/res_config.xml",
		"views/email_templates.xml",
	],
	"installable": True,
}