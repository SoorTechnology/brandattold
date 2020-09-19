# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present site-module Software Pvt. Ltd. (<https://site-module.com/>)
#    See LICENSE file for full copyright and licensing details.
###############################################################################

from odoo import api, fields, models, _
from odoo import tools
from odoo.exceptions import UserError


class update_confirmation(models.TransientModel):
	_name = "update.confirmation"

	choice = fields.Selection([('template','Product Template Only'),('variant','Product Template and Variant')], 'Update to OpenCart:', default='template')

	def update_products_confirmation(self):
		context = self.env.context.copy()
		context['choice'] = self.choice
		return self.env['opencart.sync'].with_context(context).update_products()

	def export_selected_product(self):
		choice = self.choice
		context = self.env.context.copy()
		context['choice'] = choice
		return self.env['opencart.sync'].with_context(context).export_bulk_product()

update_confirmation()
