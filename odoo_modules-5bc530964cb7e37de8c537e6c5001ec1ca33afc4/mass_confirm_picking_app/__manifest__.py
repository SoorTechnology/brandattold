# -*- coding: utf-8 -*-

{
    'name': 'Mass Validate Delivery Order from Sales',
    "author": "Edge Technologies",
    'version': '12.0.1.0',
    'live_test_url': "https://youtu.be/LwKgmaqw-WE",
    "images":['static/description/main_screenshot.png'],
    'summary': " Validate all selected sale orders delivery order in one click",
    'description': """ This app provides a functionality when user have multiple confirmed sale orders, but delivery not confirmed, user can confirm all picking for multiple sale orders very easily.While system have bulk sales orders with delivery then it's very difficult in Odoo ERP to validate each an every picking one by one. This app provides a functionality to validate all the delivery order at once. User has to select the sale orders from tree view and then validate all the pickings.Mass confirm delivery order module provide features to process the delivery order easily from the sales order action. Mass confirm delivery order mass confirm picking mass confirm sales picking mass validate delivery order mass validate picking mass validate sales picking mass process delivery order mass process picking from the sales order mass done delivery order from the sales order mass done picking from Sale order mass finished delivery order.
    """,
    "license" : "OPL-1",
    'depends': ['base','sale_management','stock'],
    'data': [
            'security/ir.model.access.csv',
            'wizards/confirm_mass_picking.xml'
            ],
    'installable': True,
    'auto_install': False,
    'price': 25,
    'currency': "EUR",
    'category': 'Warehouse',

}
