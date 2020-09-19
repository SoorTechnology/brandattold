# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present site-module Software Pvt. Ltd. (<https://site-module.com/>)
#    See LICENSE file for full copyright and licensing details.
###############################################################################

from odoo import api, fields, models, _
from odoo import tools
from odoo.exceptions import UserError


class OobConfigSettings(models.TransientModel):
    _name = 'oob.config.settings'
    _inherit = 'res.config.settings'

    oob_discount_product = fields.Many2one('product.product', string="Discount Product",
                                           help="""Service type product used for Discount purposes.""")
    oob_coupon_product = fields.Many2one('product.product', string="Coupon Product",
                                         help="""Service type product used in Coupon.""")
    oob_payment_term = fields.Many2one('account.payment.term', string="Opencart Payment Term",
                                       help="""Default Payment Term Used In Sale Order.""")
    oob_sales_team = fields.Many2one('crm.team', string="Opencart Sales Team",
                                     help="""Default Sales Team Used In Sale Order.""")
    oob_sales_person = fields.Many2one('res.users', string="Opencart Sales Person",
                                       help="""Default Sales Person Used In Sale Order.""")
    oob_sale_order_invoice = fields.Boolean(string="Invoice")
    oob_sale_order_shipment = fields.Boolean(string="Shipping")
    oob_sale_order_cancel = fields.Boolean(string="Cancel")

    @api.multi
    def set_default_fields(self):
        ir_values_obj = self.env['ir.values']
        ir_values_obj.sudo().set_default('product.product', 'oob_discount_product',
                                         self.oob_discount_product and self.oob_discount_product.id or False, True)
        ir_values_obj.sudo().set_default('product.product', 'oob_coupon_product',
                                         self.oob_coupon_product and self.oob_coupon_product.id or False, True)
        ir_values_obj.sudo().set_default('account.payment.term', 'oob_payment_term',
                                         self.oob_payment_term and self.oob_payment_term.id or False, True)
        ir_values_obj.sudo().set_default('crm.team', 'oob_sales_team',
                                         self.oob_sales_team and self.oob_sales_team.id or False, True)
        ir_values_obj.sudo().set_default('res.users', 'oob_sales_person',
                                         self.oob_sales_person and self.oob_sales_person.id or False, True)
        ir_values_obj.sudo().set_default('oob.config.settings',
                                         'oob_sale_order_shipment', self.oob_sale_order_shipment or False, True)
        ir_values_obj.sudo().set_default('oob.config.settings',
                                         'oob_sale_order_cancel', self.oob_sale_order_cancel or False, True)
        ir_values_obj.sudo().set_default('oob.config.settings',
                                         'oob_sale_order_invoice', self.oob_sale_order_invoice or False, True)
        return True

    @api.multi
    def get_default_fields(self, fields):
        ir_values_obj = self.env['ir.values']
        oob_discount_product = ir_values_obj.sudo().get_default(
            'product.product', 'oob_discount_product')
        oob_coupon_product = ir_values_obj.sudo().get_default(
            'product.product', 'oob_coupon_product')
        oob_payment_term = ir_values_obj.sudo().get_default(
            'account.payment.term', 'oob_payment_term')
        oob_sales_team = ir_values_obj.sudo().get_default('crm.team', 'oob_sales_team')
        oob_sales_person = ir_values_obj.sudo().get_default(
            'res.users', 'oob_sales_person')
        oob_sale_order_shipment = ir_values_obj.sudo().get_default(
            'oob.config.settings', 'oob_sale_order_shipment')
        oob_sale_order_cancel = ir_values_obj.sudo().get_default(
            'oob.config.settings', 'oob_sale_order_cancel')
        oob_sale_order_invoice = ir_values_obj.sudo().get_default(
            'oob.config.settings', 'oob_sale_order_invoice')
        return {
            'oob_discount_product': oob_discount_product,
            'oob_coupon_product': oob_coupon_product,
            'oob_payment_term': oob_payment_term,
            'oob_sales_team': oob_sales_team,
            'oob_sales_person': oob_sales_person,
            'oob_sale_order_shipment': oob_sale_order_shipment,
            'oob_sale_order_invoice': oob_sale_order_invoice,
            'oob_sale_order_cancel': oob_sale_order_cancel,
        }
