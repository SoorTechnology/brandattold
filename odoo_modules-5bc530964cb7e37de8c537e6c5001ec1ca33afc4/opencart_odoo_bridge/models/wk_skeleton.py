# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present site-module Software Pvt. Ltd. (<https://site-module.com/>)
#    See LICENSE file for full copyright and licensing details.
###############################################################################

from odoo import api, fields, models, _
from odoo import tools
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class WkSkeleton(models.TransientModel):
    _inherit = 'wk.skeleton'

    @api.model
    def turn_odoo_connection_off(self):
        """ To be inherited by bridge module for making connection Inactive on Odoo End"""
        res = super(WkSkeleton, self).turn_odoo_connection_off()
        active_obj = self.env['opencart.configuration'].search([('active', '=', True)])
        if active_obj:
            if active_obj[0].state == 'enable':
                active_obj[0].state = 'disable'
        return res

    @api.model
    def turn_odoo_connection_on(self):
        """ To be inherited by bridge module for making connection Active on Odoo End"""
        res = super(WkSkeleton, self).turn_odoo_connection_on()
        active_obj = self.env['opencart.configuration'].search([('active', '=', True)])
        if active_obj:
            active_obj[0].state = 'enable'
        return res

    @api.model
    def get_opencart_configuration_data(self):

        connection = self.env['opencart.configuration'].search([('active','=',True)])[0]
        oob_sales_team = connection.oob_sales_team.id
        oob_sales_person = connection.oob_sales_person.id
        oob_payment_term = connection.oob_payment_term.id

        return {'team_id': oob_sales_team, 'user_id': oob_sales_person, 'payment_term_id': oob_payment_term}

    @api.model
    def create_sale_order_line(self, data):
        context = self.env.context.copy()
        # _logger.info('............%r .................', context)
        if 'ecommerce' in context and context['ecommerce']=='opencart':
            if 'tax_id' in data:
                taxes = data.get('tax_id')
                if type(taxes) != list:
                    taxes = [data.get('tax_id')]
                data['tax_id'] = [(6, 0, taxes)]
            else:
                data['tax_id'] = False
        return super(WkSkeleton, self).create_sale_order_line(data)

    @api.model
    def get_opencart_virtual_product_id(self, data):
        erp_product_id = False
        # ir_values = self.env['ir.default']
        connection = self.env['opencart.configuration'].search([('active','=',True)])[0]
        if data['name'].startswith('S'):
            carrier_obj = self.env['sale.order'].browse(
                data['order_id']).carrier_id
            erp_product_id = carrier_obj.product_id.id
        if data['name'].startswith('D'):
            erp_product_id = connection.oob_discount_product.id
        if data['name'].startswith('V'):
            erp_product_id = connection.oob_coupon_product.id
        if not erp_product_id:
            temp_dic = {'sale_ok': False, 'name': data.get(
                'name'), 'type': 'service', 'list_price': 0.0}
            object_name = ''
            if data['name'].startswith('D'):
                object_name = 'oob_discount_product'
                temp_dic[
                    'description'] = 'Service Type product used by Opencart Odoo Bridge for Discount Purposes'
            if data['name'].startswith('V'):
                object_name = 'oob_coupon_product'
                temp_dic[
                    'description'] = 'Service Type product used by Opencart Odoo Bridge for Gift Voucher Purposes'
            erp_product_id = self.env['product.product'].create(temp_dic).id
            connection.object_name = erp_product_id
            self._cr.commit()
        return erp_product_id
