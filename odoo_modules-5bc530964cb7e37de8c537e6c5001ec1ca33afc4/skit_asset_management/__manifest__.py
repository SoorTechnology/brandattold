# -*- coding: utf-8 -*-

{
    'name': 'Odoo12 Assets Management',
    'version': '1.1',
    'summary': 'Assets Management',
    'author' : 'Srikesh Infotech',
    'license': "AGPL-3",
    'website': 'http://www.srikeshinfotech.com',
    'price'  : 40,
    'currency': 'EUR',    
    'description': """
Assets management
=================
Manage assets owned by a company or a person.
Keeps track of depreciations, and creates corresponding journal entries.

    """,
    'depends' : ['account'],
    'images': ['images/main_screenshot.png'],    
    'category': 'Accounting',    
    'qweb': [
        "static/src/xml/account_asset_template.xml",
    ],
    'data': [
        'security/account_asset_security.xml',
        'security/ir.model.access.csv',
        'wizard/asset_depreciation_confirmation_wizard_views.xml',
        'wizard/asset_modify_views.xml',
        'views/account_asset_views.xml',
        'views/account_invoice_views.xml',
        'views/account_asset_templates.xml',
        'views/product_views.xml',
        'views/res_config_settings_views.xml',
        'report/account_asset_report_views.xml',
        'data/account_asset_data.xml',
    ],
    'demo': [],    
    'installable': True,
    'auto_install': False,
    'application': True,
}
