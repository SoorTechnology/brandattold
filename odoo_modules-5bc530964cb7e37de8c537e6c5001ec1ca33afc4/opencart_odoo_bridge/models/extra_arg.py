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


class ExtraFunction(models.Model):
    _name = "extra.function"

    @api.model
    def create_pricelist(self, data):
        """create and search pricelist by any webservice like xmlrpc.
        @param code: currency code.
        @return: pricelist_id
        """
        currency_ids = self.env['res.currency'].search(
            [('name', '=', data['code'])]) or [False]
        if currency_ids:
            pricelist_ids = self.env['product.pricelist'].search(
                [('currency_id', '=', currency_ids[0].id)]) or [False]
            if pricelist_ids[0] == False:
                pricelist_dict = {
                    'name': 'Opencart_' + data['code'],
                    'active': True,
                    'currency_id': currency_ids[0].id,
                }
                pricelist_id = self.env[
                    "product.pricelist"].create(pricelist_dict)
                item_dict = {
                    'name': data['code'] + ' Public Pricelist Line',
                    'pricelist_id': pricelist_id.id,
                    'base': 'list_price',
                    'applied_on': '3_global',
                    'compute_price': 'formula',
                }
                product_pricelist_item_id = self.env[
                    'product.pricelist.item'].create(item_dict)
                return pricelist_id.id
            else:
                return pricelist_ids[0].id
        return False

    @api.model
    def _get_journal_code(self, name, sep=' '):
        name_sep_list = []
        for namp_spl in name.split(sep):
            name_sep = namp_spl.title()[0]
            if name_sep.isalnum():
                name_sep_list.append(name_sep)
        code = ''.join(name_sep_list)
        code = code[0:3]
        is_exist = self.env['account.journal'].search([('code', '=', code)])
        if is_exist:
            for i in range(1, 99):
                is_exist = self.env['account.journal'].search(
                    [('code', '=', code + str(i))])
                if not is_exist:
                    return code + str(i)[-5:]
        return code

    @api.model
    def create_payment_method(self, data):
        """create Journal by any webservice like xmlrpc.
        @param name: journal name.
        @return: payment_id
        """
        payment_id = 0
        res = self.env['account.journal'].search(
            [('type', '=', 'cash')], limit=1)
        if res:
            data['default_credit_account_id'] = res[0].default_credit_account_id.id
            data['default_debit_account_id'] = res[0].default_debit_account_id.id
            data['code'] = self._get_journal_code(data.get('name'), ' ')
            payment_id = self.env['account.journal'].create(data)
            return payment_id.id
        return False

    @api.model
    def update_quantity(self, data):
        """ Changes the Product Quantity by making a Physical Inventory.
        @param self: The object pointer.
        @param data: List of product_id and new_quantity
        @return: True
        """

        location_id = 0
        product_id = data.get('product_id')
        new_qty = data.get('new_quantity')
        ctx = dict(self._context or {})
        ctx['stock_from'] = 'opencart'
        assert product_id, _('Product ID is not set in Context')
        config_obj = self.env['opencart.configuration'].search(
            [('active', '=', True)])
        if config_obj:
            active = config_obj.active
            ctx['warehouse'] = config_obj.warehouse_id.id
            res_original = self.env['product.product'].with_context(
                ctx).browse(product_id)
            if active:
                warehouse_id = config_obj.warehouse_id.id
                location_id = config_obj.warehouse_id.lot_stock_id.id
            else:
                location_ids = self.env['stock.warehouse'].search([])
                if location_ids:
                    location_id = location_ids[0].lot_stock_id.id
            if int(new_qty) == res_original.qty_available:
                return True
            else:
                stock_data = {'product_id': product_id,
                              'location_id': location_id, 'new_quantity': new_qty}
                stock_obj = self.env[
                    'stock.change.product.qty'].create(stock_data)
                return stock_obj.with_context(ctx).change_product_qty()
        return False
