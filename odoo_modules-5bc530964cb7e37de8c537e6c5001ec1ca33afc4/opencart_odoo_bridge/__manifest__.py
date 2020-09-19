# -*- coding: utf-8 -*-
#################################################################################
# Author      : site-module Software Pvt. Ltd. (<https://site-module.com/>)
# Copyright(c): 2015-Present site-module Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.site-module.com/license.html/>
#################################################################################
{
    'name': 'An OpenCart2Odoo Connector',
    'sequence': 1,
    'summary': 'Cart2ERP Connector(C2E Connector)',
    'version': '4.2.0',
    'category': 'Generic Modules',
    'website': 'http://www.site-module.com',
    'author': 'site-module Software Pvt. Ltd.',
    'description': """
An OpenCart2Odoo Bridge.
===========================================================

This Brilliant Module will Connect Openerp with Opencart and synchronise all of your category, product, customer
----------------------------------------------------------------------------------------------------------------
and existing sales order(Invoice, shipping).
--------------------------------------------

Some of the brilliant feature of the module:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    1. synchronise all the catalog categories to Opencart.

    2. synchronise all the catalog products to Opencart.

    3. synchronise all the existing sales order(Invoice, shipping) to Opencart.

    4. Update all the store customers to Opencart.

    5. synchronise product inventory of catelog products.

NOTE : This module works very well with latest version of opencart 3.*.* and latest version of Odoo 11.0.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For any doubt or query email us at support@site-module.com or raise a Ticket on http://site-module.com/ticket/
    """,

    'depends': [
                'sale',
                'stock',
                'account',
                'delivery',
                'bridge_skeleton',
            ],
    'data': [
            'security/bridge_security.xml',
            'security/ir.model.access.csv',
            'wizard/wizard_message_view.xml',
            'wizard/status_wizard_view.xml',
            'wizard/update_confirmation_view.xml',
            'views/core_updated_files_view.xml',
            # 'views/template.xml',
            'views/opencart_odoo_sequence.xml'
        ],
    'application': True,
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
