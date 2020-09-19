#!/usr/bin/env python
# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present site-module Software Pvt. Ltd. (<https://site-module.com/>)
#    See LICENSE file for full copyright and licensing details.
###############################################################################

from odoo import api, fields, models, _
import json
from . import oobapi
from .oobapi import OpencartWebService, OpencartWebServiceDict
import logging
_logger = logging.getLogger(__name__)

################## .............opencart-odoo stock.............##################

class StockMove(models.Model):
    _inherit="stock.move"

    @api.multi
    def _action_confirm(self,merge=True,merge_into=False):
        """ Confirms stock move or put it in waiting if it's linked to another move.
        """
        res = super(StockMove, self)._action_confirm()
        oob_conf = self.env['opencart.configuration'].search([('active', '=', True)])
        if oob_conf and oob_conf.stock_type == "forecast":
            ctx = dict(self._context or {})
            self.with_context(ctx).pob_fetch_stock()
        return res
    

    @api.multi
    def _action_cancel(self):
        """ Confirms stock move or put it in waiting if it's linked to another move.
        """
        ctx = dict(self._context or {})
        ctx['action_cancel'] = True
        oob_conf = self.env['opencart.configuration'].search([('active', '=', True)])
        check = False
        for obj in self:
            if obj.state == "cancel":
                check = True
        res = super(StockMove, self)._action_cancel()
        if oob_conf and oob_conf.stock_type == "forecast" and not check:
            self.with_context(ctx).pob_fetch_stock()
        return res



    

    # @api.multi
    def _action_done(self):
        """ Makes the move done and if all moves are done, it will finish the picking.
        @return:
        """
        res = super(StockMove, self)._action_done()
        if 'stock_from' in self._context and self._context['stock_from'] == 'opencart':
            return res
        oob_conf = self.env['opencart.configuration'].search([('active', '=', True)])
        if oob_conf and oob_conf.stock_type == "onhand":
            ctx = dict(self._context or {})
            self.with_context(ctx).pob_fetch_stock()    
        return True
    
    def pob_fetch_stock(self):
        for rec in self:
            flag = 1
            data = rec
            product_pool = self.env['product.product']
            if data.origin!=False:
                if data.picking_type_id:
                    type_obj = self.env['stock.picking.type'].browse(data.picking_type_id.id)
                if data.origin.startswith('SO') and type_obj.code=='outgoing':
                    sale_id = self.env['sale.order'].search([('name','=',data.origin)])
                    if sale_id:
                        get_channel = sale_id[0].ecommerce_channel
                        if get_channel == 'opencart':
                            flag = 0
            if flag:
                erp_product_id = data.product_id.id
                product_obj = product_pool.browse(erp_product_id)
                product_qty = self.env['opencart.configuration'].get_quantity(product_obj) 
                template_qty = self.env['opencart.configuration'].get_quantity(product_obj.product_tmpl_id)
                self.synch_quantity(erp_product_id, product_qty, template_qty)
        return True

    def synch_quantity(self, erp_product_id, product_qty, template_qty):
        response = self.update_quantity(erp_product_id, product_qty, template_qty)
        if response[0] == 1:
            return True

    def update_quantity(self, erp_product_id, variant_qty, template_qty):
        qty = 0
        session = 0
        text = ''
        stock = 0
        product_pool = self.env['opencart.product']
        check_mapping = product_pool.sudo().search([('product_name','=',erp_product_id)])
        if check_mapping:
            map_obj = check_mapping[0]
            oc_product_id = map_obj.oc_product_id
            oc_option_id = map_obj.oc_option_id
            connection = self.env['opencart.configuration'].sudo()._create_connection()
            if connection:
                url = connection[2]
                session = connection[0]
                session_key = connection[1]
                if not session:
                    return [0,text]
                else:
                    params={}
                    route = 'UpdateProductStock'
                    params['stock'] = template_qty
                    params['product_id'] = oc_product_id
                    if oc_option_id != 0:
                        params['option_id'] = oc_option_id
                        params['option_qty'] = variant_qty
                    params['session'] = session_key
                    resp = session.get_session_key(url+route, params)
                    resp = resp.json()
                    key = str(resp[0])
                    status = resp[1]
                    if not status:
                        _logger.info('###### Stock Update resp: %r ##################', str(key))
                        return [0,str(key)]
                    return [1, True]
        else:
            return [0,'Error in Updating Stock, Product Id %s not mapped.'%erp_product_id]
# StockMove()
