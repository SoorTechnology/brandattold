# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'Stock Inventory Adjustments Import Using CSV',
    'version': '1.2',
    'price': 40.0,
    'author' : 'Probuse Consulting Service Pvt. Ltd.',
    'website' : 'www.probuse.com',
    'support': 'contact@probuse.com',
    'currency': 'EUR',
    'license': 'Other proprietary',
    'live_test_url': 'https://youtu.be/gYzPzaTFR9k',
    'images': ['static/description/image1.png'],
    'category': 'Warehouse',
    'summary':  'Stock Inventory Adjustments Import using CSV',
    'depends': ['stock','sale'],
    'description': """
    This module add feature to import stock inventory in inventory adjustments line using CSV File.
    Import Inventory Details
    Import Inventory through CSV file
inventory Adjustments
stock Adjustments
stock inventory
import csv Adjustments
import inventory
import stock
import csv file
stock csv
excel stock
Stock Inventory Adjustments Import Using CSV File

This module will import stock inventory adjustments using csv.
You have to prepare CSV file with product code / internal reference and import it.
This module only support import feature. For update inventory you have to export and import usind Odoo import/export feature.
import Inventory
Inventory import
    """,
    'data': [
         'wizard/stock_inventory_import_wizard.xml',
         'views/stock_inventory_import_view.xml',
     ],
    'installable': True,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
