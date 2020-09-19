# -*- coding:utf-8 -*-
{
	'name' : 'Import Purchase Order Line from Excel',
	'version': '1.0',
    'price': 25.0,
    'author' : 'Probuse Consulting Service Pvt. Ltd.',
    'website' : 'www.probuse.com',
    'currency': 'EUR',
    'license': 'Other proprietary',
	'category': 'Purchases',
	'summary':  """This module import purchase order line from excel file.""",
	'description': """
    Purchase Order Line Import Excel
This module import purchase order line from excel file.
Import purchase Order Line from Excel
This module import purchase order line from excel file.

purchase order import
purchase line import
purchase order line import
purchase order line excel import
import purchase order excel
import sale order excel
import purchase order data
import excel purchase order line
import excel purchase order
import so
import so lines
import order from excel
import order from xls
purchase quotation import
    """,
    'images': ['static/description/xls_import.png'],
    'external_dependencies': {'python': ['xlrd']},
	'depends': ['purchase'],
	'data': [
	    'wizard/purchase_line_import.xml',
		'views/purchase_view.xml',
	],
	'installable' : True,
	'application' : True,
	'auto_install' : False,
}




