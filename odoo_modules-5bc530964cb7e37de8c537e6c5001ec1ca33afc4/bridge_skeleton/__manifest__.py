# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2015-Present site-module Software Pvt. Ltd. (<https://site-module.com/>)
#   See LICENSE file for full copyright and licensing details.
#
#################################################################################

{
    'name': 'Odoo: Bridge Skeleton',
    'version': '1.1.0',
    'author': 'site-module Software Pvt. Ltd.',
    'summary': 'Core of site-module Bridge Modules',
    'description': """
        This is core for all basic operations features provided in site-module's Bridge Modules.
    """,
    'website': 'http://www.site-module.com',
    'images': [],
    'depends': ['sale','stock','account','account_cancel','delivery'],
    'category': 'POB',
    'sequence': 1,
    'data': ['views/inherited_view.xml'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
