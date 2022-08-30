{
    "name": "RMinds Vendor Review Alert",
    "version": "14.0.1.1.0",
    "category": "RMinds/Purchase",
    "license": "AGPL-3",
    "summary": "This Module will help in Vendor Review Yearly and Reminder Next Review",
    "author": "Manoj Parmar",
    "maintainers": ["Manoj Parmar"],
    "website": "www.rminds.com",
    "depends": ["base","purchase","mail"],
    "data": [
        "security/ir.model.access.csv",
        "views/res_partner.xml",
        "views/vendor_review_log.xml",
        "views/res_config_settings_view.xml",
        "data/vendor_review_cron.xml",
        "data/vendor_review_mail_template.xml",
        
    ],
    "installable": True,
    "application": True,
}
