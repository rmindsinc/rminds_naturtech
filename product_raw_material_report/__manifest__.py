{
	"name": "Product Raw Report",
	"description": "Display Raw material utilizations and purchase details of Product",
	"depends": ['sale','purchase'],
	"data": [
			"security/ir.model.access.csv",
			'wizard/product_raw_wizard.xml',
			'report/report_product_raw_material.xml'
	],
	"installable": True,
}