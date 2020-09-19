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
# If not, see <https://site-module.com/>
#################################################################################
{
    'name': 'Opencart-Odoo Stock Management',
    'version': '3.4.0',
    'category': 'Generic Modules',
    'sequence': 6,
    'summary': 'Manage Stock with Opencart Connector',
    'description': """
    This Module helps in maintaining stock between odoo and opencart with real time.

	NOTE : This module works very well with latest version of opencart 3.*.* and latest version of Odoo 12.0.
    """,
    'author': 'site-module Software Pvt Ltd.',
    'depends': ['opencart_odoo_bridge'],
    'website': 'http://www.site-module.com',
    'data': ['views/opencart_odoo_stock_view.xml'],
    'application': True,
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
