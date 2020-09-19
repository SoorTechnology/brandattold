# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name" : "Import Stock Inventory Adjustment from CSV/Excel file",
    "author" : "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "support": "info@softhealer.com",       
    "category": "Warehouse",
    "summary": "This module useful to import stock inventory from csv/excel.",
    "description": """
    
 This module useful to import stock inventory from csv/excel. 

 

                    """,    
    "version":"12.0.2",
    "depends" : ["base","sh_message","stock","product"],
    "application" : True,
    "data" : [
        
            'security/import_inventory_security.xml',
            'wizard/import_inventory_wizard.xml',
            'views/stock_view.xml',
            
            ],         
    'external_dependencies' : {
        'python' : ['xlrd'],
    },                  
    "images": ["static/description/background.png",],              
    "auto_install":False,
    "installable" : True,
    "price": 18,
    "currency": "EUR"   
}
