# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present site-module Software Pvt. Ltd. (<https://site-module.com/>)
#    See LICENSE file for full copyright and licensing details.
###############################################################################

from odoo import api, fields, models, _
from odoo import tools
from odoo.exceptions import UserError

import time




class wizard_message(models.TransientModel):
	_name = "wizard.message"

	# _columns={
	text = fields.Text('Message')
	         # }
# wizard_message()
