# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present site-module Software Pvt. Ltd. (<https://site-module.com/>)
#    See LICENSE file for full copyright and licensing details.
###############################################################################

############## Overide Core classes for maintaining OpenCart Information #################
from odoo import api, fields, models, _
from odoo import tools
from odoo.exceptions import UserError
from odoo.tools.translate import _
import json
from . import oobapi
from .oobapi import OpencartWebService, OpencartWebServiceDict
from .core_updated_files import API_PATH
from .core_updated_files import _unescape
import logging
_logger = logging.getLogger(__name__)

class ProductAttribute(models.Model):
    _inherit = 'product.attribute'

    @api.model
    def create(self, vals):
        if 'opencart' in self._context:
            if 'name' in vals:
                vals['name'] = _unescape(vals['name'])
            erp_id =  super(ProductAttribute, self).create(vals)
            if erp_id:
                mapping_data = {
                        'name':erp_id.id,
                        'erp_id':erp_id.id,
                        'opencart_id':self._context['opencart_id']
                    }
                self.env['opencart.product.option'].create(mapping_data)
        else:
            erp_id =  super(ProductAttribute, self).create(vals)
        return erp_id

    @api.multi
    def write(self, vals):
        if 'opencart' in self._context:
            if 'name' in vals:
                vals['name'] = _unescape(vals['name'])
        return super(ProductAttribute, self).write(vals)
ProductAttribute()

class ProductAttributeValue(models.Model):
    _inherit = 'product.attribute.value'

    @api.model
    def create(self, vals):
        if 'opencart' in self._context:
            if 'name' in vals:
                vals['name'] = _unescape(vals['name'])
            erp_id =  super(ProductAttributeValue, self).create(vals)
            if erp_id:
                mapping_data = {
                        'name':erp_id.id,
                        'erp_id':erp_id.id,
                        'opencart_value_id':self._context['opencart_id'],
                        'erp_attr_id':vals['attribute_id'],
                        'opencart_option_id':self._context['oc_attr_id']
                    }
                self.env['opencart.product.option.value'].create(mapping_data)
        else:
            erp_id =  super(ProductAttributeValue, self).create(vals)
        return erp_id

    @api.multi
    def write(self, vals):
        if 'opencart' in self._context:
            if 'name' in vals:
                vals['name'] = _unescape(vals['name'])
        return super(ProductAttributeValue,self).write(vals)

ProductAttributeValue()

class ProductCategory(models.Model):
    _inherit= 'product.category'

    @api.model
    def create(self, vals):
        if 'opencart' in self._context:
            if 'name' in vals:
                vals['name'] = _unescape(vals['name'])
        cat_id = super(ProductCategory, self).create(vals)
        if 'opencart' in self._context:
            if cat_id:
                self.env['opencart.product.category'].create({
                    'odoo_id':cat_id.id,
                    'ecommerce_cat_id':int(vals['opencart_id']),
                    'created_by':'Opencart'
                })
        return cat_id

    @api.multi
    def write(self, vals):
        if 'opencart' in self._context:
            if 'name' in vals:
                vals['name'] = _unescape(vals['name'])
        else:
            opncart_category = self.env['opencart.product.category'].sudo().search([('odoo_id','=',self.id)])
            if opncart_category:
                opncart_category[0].sudo().need_sync = 'yes'
        return super(ProductCategory,self).write(vals)

ProductCategory()

class ResPartner(models.Model):
    _inherit= 'res.partner'

    @api.model
    def create(self, vals):
        if 'opencart' in self._context:
            if 'name' in vals:
                vals['name'] = _unescape(vals['name'])
            if 'street' in vals:
                vals['street'] = _unescape(vals['street'])
            if 'street2' in vals:
                vals['street2'] = _unescape(vals['street2'])
            if 'city' in vals:
                vals['city'] = _unescape(vals['city'])
            if 'email' in vals:
                vals['email'] = _unescape(vals['email'])
        partner = super(ResPartner, self).create(vals)
        return partner

    @api.multi
    def write(self, vals):
        if 'opencart' in self._context:
            if 'name' in vals:
                vals['name'] = _unescape(vals['name'])
            if 'street' in vals:
                vals['street'] = _unescape(vals['street'])
            if 'street2' in vals:
                vals['street2'] = _unescape(vals['street2'])
            if 'city' in vals:
                vals['city'] = _unescape(vals['city'])
            if 'email' in vals:
                vals['email'] = _unescape(vals['email'])
        return super(ResPartner, self).write(vals)

ResPartner()

class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    @api.model
    def create(self, vals):
        context = self.env.context.copy()
        if 'opencart' in vals:
            context['ecommerce'] = "opencart"
            context['type'] = 'shipping'
            product_id = self.env['wk.skeleton'].with_context(context).get_opencart_virtual_product_id(vals)
            vals['name'] = _unescape(vals['name'])
            temp = self.env['res.users'].browse(self._uid)
            vals['partner_id'] = temp.company_id
            vals['product_type'] = 'service'
            vals['taxes_id'] = False
            vals['product_id'] = product_id
            vals['supplier_taxes_id'] = False
        return super(DeliveryCarrier, self).create(vals)

class SaleOrder(models.Model):
    _inherit= 'sale.order'

    opencart_id = fields.Integer(string='OpenCart Order Id')

    @api.model
    def _get_ecommerces(self):
        res = super(SaleOrder, self)._get_ecommerces()
        res.append(('opencart','Opencart'))
        return res

    @api.one
    def action_cancel(self):
        res = super(SaleOrder, self).action_cancel()
        if 'opencart' not in self._context:
            res = self.manual_opencart_order_status_operation("cancel")
        return res

    @api.one
    def manual_opencart_order_status_operation(self, operation):
        text = ''
        status = 'no'
        session = False
        mage_shipment = False
        mapping_ids = self.env['wk.order.mapping'].sudo().search([('erp_order_id','=', self.id)])
        if mapping_ids:
            mapping_obj = mapping_ids[0]
            oc_order_id = mapping_obj.ecommerce_order_id
            connection = self.env['opencart.configuration'].sudo()._create_connection()
            if connection:
                url = connection[2]
                session = connection[0]
                session_key = connection[1]
                if session and oc_order_id:
                    data = {}
                    data['order_id'] =  oc_order_id
                    route = 'UpdateOrderStatus'
                    data['session'] =  session_key
                    if operation == "shipment":
                        data['order_status_id'] =  'delivered'
                    elif operation == "cancel":
                        data['order_status_id'] =  'cancel'
                    elif operation == "invoice":
                        data['order_status_id'] =  'paid'
                    data = json.dumps(data)
                    resp = session.get_session_key(url+route, data)
                    _logger.info('.......... %r ..............', resp)
                    resp = resp.json()
                    key = str(resp[0])
                    status = resp[1]
                    if status:
                        return True
                    return str(key)
        return True

    def manual_opencart_paid(self):
        text = ''
        session = 0
        route = 'UpdateOrderStatus'
        oc_invoice = False
        param = {}
        connection = self.env['opencart.configuration'].sudo()._create_connection()
        if connection:
            url = connection[2]
            session = connection[0]
            session_key = connection[1]
            if session:
                map_id = self.env['wk.order.mapping'].sudo().search([('erp_order_id','=',self._ids[0])])
                if map_id:
                    map_obj = map_id[0]
                    oc_order_id = map_obj.ecommerce_order_id
                    data={}
                    data['order_id'] =  oc_order_id
                    data['session'] = session_key
                    data['order_status_id'] = 'paid'
                    data = json.dumps(data)
                    resp = session.get_session_key(url+route, data)
                    resp = resp.json()
                    key = str(resp[0])
                    status = resp[1]
                    if status:
                        return True
                    return str(key)
        # self._cr.commit()
        return True

SaleOrder()


class account_payment(models.Model):
    _inherit = "account.payment"


    @api.multi
    def post(self):
        res = super(account_payment, self).post()
        if 'opencart' not in self._context:
            sale_obj = self.env['sale.order']
            for rec in self:
                invoice_ids = rec.invoice_ids
                for inv_obj in invoice_ids:
                    invoices = inv_obj.read(['origin', 'state'])
                    if invoices[0]['origin']:
                        sale_ids = sale_obj.search(
                            [('name', '=', invoices[0]['origin'])])
                        for sale_order_obj in sale_ids:
                            order_id = self.env['wk.order.mapping'].sudo().search(
                                [('erp_order_id', '=', sale_order_obj.id)])
                            if order_id and sale_order_obj.ecommerce_channel == "opencart" and sale_order_obj.is_invoiced:
                                sale_order_obj.sudo().manual_opencart_paid()
        return res

class Picking(models.Model):
    _name = "stock.picking"
    _inherit = "stock.picking"


    @api.multi
    def action_done(self):
        res = super(Picking, self).action_done()
        _logger.info('/......Action_Done.... %r ............', self._context)
        if 'opencart' not in self._context:
            order_name = self.browse(self._ids[0]).origin
            sale_id = self.env['sale.order'].search([('name','=',order_name)])
            if len(sale_id):
                sale_id.sudo().manual_opencart_order_status_operation('shipment')
        return True

class WkSkeleton(models.TransientModel):
    _inherit = "wk.skeleton"

    def get_opencart_virtual_product_id(self, order_line):
        if 'ecommerce' in self._context and self._context['ecommerce'] == "opencart":
            if 'type' in self._context and self._context['type'] == 'shipping':
                carrier = self._context.get('carrier_id', False)
                if carrier:
                    obj = self.env['delivery.carrier'].browse(carrier)
                    erp_product_id = obj.product_id.id
        return erp_product_id
# class account_invoice(models.Model):
#     _name = 'account.invoice'
#     _inherit='account.invoice'

#     def manual_opencart_invoice(self):
#         text = ''
#         session = 0
#         oc_invoice = False
#         param = {}
#         connection = self.env['opencart.configuration'].search([('active','=',True)])
#         if connection:
#             config_obj = connection[0]
#             url = config_obj.api_url+'/api/server.php'
#             param['api_user'] = config_obj.api_user
#             param['api_key'] = config_obj.api_key
#             try:
#                 server = SOAPpy.SOAPProxy(url)
#                 session = server.login(param)
#             except:
#                 pass
#             if session:
#                 map_id = self.env['sale.order'].search([('id','in',self._ids),('opencart_id','!=',False)])
#                 if map_id:
#                     map_obj = map_id[0]
#                     oc_order_id = map_obj.opencart_id
#                     data={}
#                     data['order_id'] =  oc_order_id
#                     data['order_status_id'] = 'paid'
#                     try:
#                         server = SOAPpy.SOAPProxy(url)
#                         oc_invoice = server.UpdateOrderStaus(session, data)
#                     except Exception,e:
#                         return str(e)
#         self._cr.commit()
#         return oc_invoice

#     def write(self, vals):
#         context = self.env.context.copy()
#         ids = self._ids
#         if isinstance(ids, (int, long)):
#             ids = [ids]
#         ######## manual_opencart_invoice method is used to update an invoice status on opencart end #########
#         for id in ids:
#             if vals.has_key('state'):
#                 if vals['state'] == 'paid':
#                     invoice_origin = self.browse(id).origin
#                     sale_origin_id = self.env['sale.order'].search([('name','=',invoice_origin)])
#                     if sale_origin_id:
#                         oc_invoice = sale_origin_id.manual_opencart_invoice()
#         return super(account_invoice,self).write(cr,uid,ids,vals,context=context)
#         ###################################################
# account_invoice()
