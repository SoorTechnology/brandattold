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
import xmlrpc.client
import logging
_logger = logging.getLogger(__name__)

################ Mapping update Model(Used from server action) ################

class mapping_update(models.TransientModel):
	_name = "mapping.update"

	need_sync = fields.Selection([('yes', 'Yes'),('no', 'No')],'Update Required')

	@api.multi
	def open_update_wizard(self):
		_logger.info('................. %r ...............', [self, self.env.context])
		partial = self.create(self.env.context)
		_logger.info('..............Partial... %r ...............', [partial])
		return { 'name':_("Bulk Action"),
				 'view_mode': 'form',
				 'view_id': False,
				 'view_type': 'form',
				 'res_model': 'mapping.update',
				 'res_id': partial.id,
				 'type': 'ir.actions.act_window',
				 'nodestroy': True,
				 'target': 'new',
				 'context':self._context,
				 'domain': '[]',
			}

	@api.multi
	def update_mapping_status(self):
		count = 0
		context = self.env.context.copy()
		model = context.get('active_model')
		active_ids = context.get('active_ids')
		status = self.need_sync
		for i in active_ids:
			check = self.env['opencart.product.template'].search([('erp_template_id', '=', i)])
			check.write({'need_sync':status}) if check else check
			count = count+1
		text = 'Status of %s record has been successfully updated to %s.'%(count,status)
		partial = self.env['wizard.message'].create({'text':text})
		return { 'name':_("Information"),
				 'view_mode': 'form',
				 'view_id': False,
				 'view_type': 'form',
				'res_model': 'wizard.message',
				 'res_id': partial.id,
				 'type': 'ir.actions.act_window',
				 'nodestroy': True,
				 'target': 'new',
			 }
