# -*- coding: utf-8 -*-

from odoo import models,fields,api , _
from odoo.exceptions import UserError, ValidationError

class ConfirmPickingSale(models.Model):
	_name = 'mass.confirm'

	@api.multi
	def mass_confirm(self,vals):
		order_ids=[]
		model = None
		
		for i in vals:
			order_ids.append(i['data']['id'])
			model = i['model']
		orders = self.env[model].browse(order_ids)
		
		if ( model == "sale.order"):
			for order in orders: 
				if (order.state == "sale"):
					for i in order.picking_ids:
						if (i.state != "done"):
							for move in i.move_line_ids:
								move.write({'qty_done':move.product_uom_qty})
							for move_line in i.move_lines:
								move_line.write({'quantity_done': move_line.product_uom_qty})
							i.button_validate()
		
		else:
			raise UserError(_('This Funcationality Only works in sale orders'))
		return

	
