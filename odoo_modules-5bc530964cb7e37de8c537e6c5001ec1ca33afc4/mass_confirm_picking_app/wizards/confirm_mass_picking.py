# -*- coding: utf-8 -*-

import time
from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError

class StockPickingSuccess(models.TransientModel):
	_name = "stock.picking.success"
	_description = "Confirm All Selected Picking"

class StockPickingConfirm(models.Model):
	_name = "stock.picking.confirm"
	_description = "Confirm All Selected Picking"

	sale_orders = fields.Char(string="sale orders name"	)

	@api.model
	def default_get(self, fields):
		res = super(StockPickingConfirm, self).default_get(fields)
		sale_orders = self.env['sale.order'].browse(self._context.get('active_ids', []))
		orders = []
		for i in sale_orders:
			orders.append(i.name)
		if orders:
			res.update({
				'sale_orders' : ','.join(orders)
				})
		return res

	@api.multi
	def mass_confirm(self):
		sale_orders = self.env['sale.order'].browse(self._context.get('active_ids', []))
		count = 0 

		for i in sale_orders:
			if i.state == "draft":
				count = 1
				return {
					'name':_('Picking Validation Fail'),
					'view_type':'form',
					'view_mode':'form',
					'res_model':'stock.picking.success',
					'view_id':self.env.ref('mass_confirm_picking_app.validate_picking_Fails_wizard').id,
					'type' : 'ir.actions.act_window',
					'target':'new'
					}

		for order in sale_orders:
			for picking in order.picking_ids:
				if picking.state == "done":
					count = 1
					return {
						'name':_('Picking Validation Fail'),
						'view_type':'form',
						'view_mode':'form',
						'res_model':'stock.picking.success',
						'view_id':self.env.ref('mass_confirm_picking_app.validate_picking_details_Fails_wizard').id,
						'type' : 'ir.actions.act_window',
						'target':'new'
						}

		if count == 0:
			for order in sale_orders:
				if (order.state == "sale"):
					for i in order.picking_ids:
						if (i.state != "done"):
							for move in i.move_line_ids:
								move.write({'qty_done':move.product_uom_qty})
							for move_line in i.move_lines:
								move_line.write({'quantity_done': move_line.product_uom_qty})
							i.button_validate()

			return {
					'name':_('Picking Validation Confirmation'),
					'view_type':'form',
					'view_mode':'form',
					'res_model':'stock.picking.success',
					'view_id':self.env.ref('mass_confirm_picking_app.validate_picking_success_wizard').id,
					'type' : 'ir.actions.act_window',
					'target':'new'
					}
