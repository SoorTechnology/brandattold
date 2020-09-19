# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present site-module Software Pvt. Ltd. (<https://site-module.com/>)
#    See LICENSE file for full copyright and licensing details.
###############################################################################

from odoo import api, fields, models, _
from odoo import tools
from odoo.exceptions import UserError
from odoo.tools.translate import _
import json
import base64
from base64 import b64encode
from . import oobapi
from .oobapi import OpencartWebService, OpencartWebServiceDict
import logging
_logger = logging.getLogger(__name__)

API_PATH = '/index.php?route=api/oob/'


def _unescape(text):
    ##
    # Replaces all encoded characters by urlib with plain utf8 string.
    #
    # @param text source text.
    # @return The plain text.
    from urllib.parse import unquote
    try:
        temp = unquote(text.encode('utf8'))
    except Exception as e:
        temp = text
    return temp


def _decode(name):
    name = urllib.parse.unquote(name)
    decoded_name = name
    if isinstance(name, str):
        try:
            decoded_name = name.encode('utf8')
        except:
            decoded_name = name
    else:
        try:
            decoded_name = str(name, 'utf8')
        except:
            try:
                decoded_name = str(name, 'latin1').encode('utf8')
            except:
                decoded_name = name
    return decoded_name

############## OpenCart Credentials class #################


class opencart_configuration(models.Model):
    _name = "opencart.configuration"

    def _get_default_category(self):
        cat_ids = self.env['product.category'].search([])
        if not cat_ids:
            raise UserError(_('There is no category found on your Odoo ! Please create one.'))
        return cat_ids[0]

    @api.one
    def _get_count(self):
        domain = []
        products = self.env['opencart.product.template'].search_count(domain)
        categories = self.env['opencart.product.category'].search_count(domain)
        orders = self.env['wk.order.mapping'].search_count(domain)
        customers = self.env['opencart.customer'].search_count(domain)
        self.opencart_products = (products)
        self.opencart_categories = (categories)
        self.opencart_orders = (orders)
        self.opencart_customers = (customers)

    @api.model
    def create(self, vals):
        active_ids = self.env['opencart.configuration'].search([('active', '=', True)])
        if vals['active'] is True:
            if active_ids:
                raise UserError(_("Sorry, Only one active connection is allowed."))
        return super(opencart_configuration, self).create(vals)

    @api.multi
    def write(self, vals):
        active_ids = self.env['opencart.configuration'].search([('active', '=', True)])
        if 'active' in vals:
            if vals['active'] is True:
                if len(active_ids) > 1:
                    raise UserError(_("Sorry, Only one active connection is allowed."))
        return super(opencart_configuration, self).write(vals)

    name = fields.Char('Connection Name', default='Opencart Connection')
    api_url = fields.Char('Root URL', size=100, help="e.g:-'http://www.opencart.com/upload'")
    api_user = fields.Char('User')
    connection_status = fields.Boolean(
        string="Connection Status", default=False)
    api_key = fields.Text('Api Key', size=255)
    status = fields.Char('Connection Status', readonly=True, size=255)
    active = fields.Boolean('Active', default=lambda *a: 1)
    oc_default_category = fields.Many2one('product.category', 'Default Category', required=True, default=_get_default_category)
    session_key = fields.Char('Opencart api token', readonly=1)
    warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse',
                                    help="Used During Inventory Synchronization From Opencart to Odoo.")
    location_id = fields.Many2one(related = 'warehouse_id.lot_stock_id', type="many2one", string="Stock Location", readonly=True)
    state = fields.Selection([('enable', 'Enable'), ('disable', 'Disable')], string='Status', help="status will be consider during order invoice, order delivery and order cancel, to stop asynchronous process at other end.", default='enable', size=100)
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
    
    stock_type = fields.Selection([('forecast','Forecast Quantity'),('onhand','On-Hand Quantity')],string="Stock Type",default='onhand', size=100)

    opencart_products = fields.Integer(
        compute='_get_count'
    )
    opencart_categories = fields.Integer(
        compute='_get_count'
    )
    opencart_orders = fields.Integer(
        compute='_get_count'
    )
    opencart_customers = fields.Integer(
        compute='_get_count'
    )

    @api.multi
    def test_connection(self):
        text = 'Test connection Un-successful please check the opencart api credentials!!!'
        status = 'OpenCart Connection Un-successful'
        param = {}
        route = 'login'
        session = ''
        url = self.api_url + API_PATH
        # param['username'] = self.api_user
        param['api_key'] = self.api_key
        opencart = OpencartWebServiceDict()
        resp = opencart.get_session_key(url+route, param)
        # _logger.info('..... %r............ ', [resp, resp.content])
        status_code = resp.status_code
        if status_code in [200, 201]:
            resp = resp.json()
            if isinstance(resp, list) and resp[1]:
                key = str(resp[0])
                status = resp[1]
                if status:
                    self.write({'session_key':key})
                    text = 'Test Connection with opencart is successful, now you can proceed with synchronization.'
                    status = "Congratulation, It's Successfully Connected with OpenCart Api."
                    self.status = status
                    self.connection_status = True
                else:
                    text += '\n %r'%key
                    self.connection_status = False
            else:
                self.status = status
                self.session_key = False
                self.connection_status = False
                text = "%r \n%r \n"%(status_code, text)
                if 'error' in resp:
                    text += resp['error']['ip']+'\n' + resp['error']['key']
        partial = self.env['wizard.message'].create({'text': text})
        return {'name': _("Information"),
                'view_mode': 'form',
                'view_id': False,
                'view_type': 'form',
                'res_model': 'wizard.message',
                'res_id': partial.id,
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'new',
                'domain': '[]',
                }
    
    @api.multi
    def get_quantity(self,obj_pro):
        qty = 0.0
        config_id = self.search([('active','=',True)])
        if config_id and len(config_id)==1:
            if config_id.stock_type =="onhand":
                qty = obj_pro.qty_available or 0.0
            else:
                qty = obj_pro.virtual_available or 0.0
        return qty

    @api.model
    def _create_connection(self):
        config_id = self.search([('active', '=', True)])
        if len(config_id) > 1:
            raise UserError(_(
                "Sorry, only one Active Configuration setting is allowed."))
        if not config_id:
            raise UserError(_(
                "Please create the configuration part for OpenCart connection!!!"))
        else:
            param = {}
            session = config_id.session_key
            url = config_id[0].api_url + API_PATH
            # param['api_user'] = config_id[0].api_user
            # param['api_key'] = config_id[0].api_key
        # try:
            opencart = OpencartWebServiceDict()
            # session = server.login(param)
        # except Exception as e:
            # raise UserError(_("OpenCart Error " + " in connection: %s") % e)
            if session:
                return [opencart, session, url]
            else:
                return False

    @api.multi
    def open_mapping_view(self):
        self.ensure_one()
        res_model = self._context.get('mapping_model')
        domain = self._context.get('domain')
        # domain = []
        mapping_ids = self.env[res_model].search(domain).ids
        return {
            'name': ('Mapping'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': res_model,
            'view_id': False,
            'domain': [('id', 'in', mapping_ids)],
            'target': 'current',
        }

    @api.multi
    def export_products(self):
        return self.env['opencart.sync'].export_products()

    @api.multi
    def update_category(self):
        return self.env['opencart.sync'].update_category()

    @api.multi
    def export_category(self):
        return self.env['opencart.sync'].export_category()



############ .............Synchronization.............###########


class opencart_sync(models.Model):
    _name = 'opencart.sync'

    @api.multi
    def open_configuration(self):
        view_id = False
        setting_ids = self.env['opencart.configuration'].search([('active', '=', True)])
        if setting_ids:
            view_id = setting_ids[0].id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Configure OpenCart Api',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'opencart.configuration',
            'res_id': view_id,
            'target': 'current',
            'domain': '[]',
        }

    @api.multi
    def _update_specific_category(self, id, session_key, session, url):
        get_category_data = {}
        route = 'category'
        cat = ''
        cat_pool = self.env['product.category']
        cat_pool_opn = self.env['opencart.product.category'].search([('odoo_id','=',id)])
        if cat_pool_opn:
            oc_cat_id = cat_pool_opn.ecommerce_cat_id
        cat_obj = cat_pool.browse(id)
        cat_id = cat_obj.id
        parent_id = cat_obj.parent_id.id or False
        get_category_data['category_id'] = oc_cat_id
        get_category_data['session'] = session_key
        get_category_data['name'] = cat_obj.name
        if parent_id:
            obj_cat = self.env['opencart.product.category'].search([('odoo_id','=',parent_id)])
            oc_parent_id = obj_cat.ecommerce_cat_id or False
            cat_obj = cat_pool.browse(parent_id)
            if oc_parent_id:
                get_category_data['parent_id'] = oc_parent_id
            else:
                oc_cat_id = self.sync_categories(
                    session_key, session, url, cat_obj.parent_id)
                get_category_data['parent_id'] = oc_cat_id
        else:
            get_category_data['parent_id'] = 0
    # try:
        resp = session.get_session_key(url+route, get_category_data)
        resp = resp.json()
        key = str(resp[0])
        status = resp[1]
        if status:
            cat_pool_opn.write({'need_sync': 'no'})
            return [1, 'Updated successfully']
    # except Exception as e:
        return [0, key]

        ########## update category ##########

    @api.multi
    def update_category(self):
        text = text1 = ''
        up_error_ids = []
        success_ids = []
        connection = self.env['opencart.configuration']._create_connection()
        if connection:
            url = connection[2]
            session = connection[0]
            session_key = connection[1]
            cat_ids = self.env['opencart.product.category'].search([('need_sync', '=', 'yes')])
            if not cat_ids:
                raise UserError(_("No category(s) has been found to be Update on OpenCart!!!"))
            if cat_ids:
                for i in cat_ids:
                    cat_update = self._update_specific_category(i.odoo_id.id, session_key, session, url)
                    if cat_update[0] != 0:
                        success_ids.append(i.odoo_id.id)
                    else:
                        up_error_ids.append(cat_update[1])
                if success_ids:
                    text = 'List of %s Category ids has been sucessfully updated to OpenCart. \n' % success_ids
                if up_error_ids:
                    text1 = 'The Listed Category ids %s does not updated on OpenCart.' % up_error_ids
                partial = self.env['wizard.message'].create({'text': text + text1})
                return {'name': _("Information"),
                        'view_mode': 'form',
                        'view_id': False,
                        'view_type': 'form',
                        'res_model': 'wizard.message',
                        'res_id': partial.id,
                        'type': 'ir.actions.act_window',
                        'nodestroy': True,
                        'target': 'new',
                        'domain': '[]',
                        }

    @api.model
    def create_category(self, url, session, session_key, catg_id, parent_id, catgname):
        cat = parent_id
        opencart_cat_id = 0
        route = 'category'
        catgdetail = dict({
            'name': catgname,
            'parent_id': parent_id,
            'erp_category_id': catg_id.id
        })
        catgdetail['session'] = session_key
        if catg_id.id > 0:
        # try:
            resp = session.get_session_key(url+route, catgdetail)
            # _logger.info('........... %r ..........', resp.content)
            # _logger.info('...........Data: %r ..........', catgdetail)
            resp = resp.json()
            key = str(resp[0])
            oc_id = resp[1]
            status = resp[2]
            if status:
                opencart_cat_id = oc_id
            else:
                return [0, key]
        else:
            return False
        if opencart_cat_id:
            self.env['opencart.product.category'].create({
                    'odoo_id':catg_id.id,
                    'ecommerce_cat_id':int(opencart_cat_id),
                    'created_by':'Odoo'
                })
            return opencart_cat_id

    def sync_categories(self, session_key, session, url, cat_id):
        open_check = self.env['opencart.product.category'].search([('odoo_id', '=', cat_id.id)])
        if not open_check:
            obj_catg = cat_id
            name = obj_catg.name
            if obj_catg.parent_id.id:
                p_cat_id = self.sync_categories(
                    session_key, session, url, obj_catg.parent_id)
            else:
                p_cat_id = self.create_category(
                    url, session, session_key, cat_id, 0, name)
                return p_cat_id
            category_id = self.create_category(
                url, session, session_key,cat_id, p_cat_id, name)
            return category_id
        else:
            cart_id = open_check.ecommerce_cat_id
            return cart_id

    @api.multi
    def export_category(self):
        length = []
        map_id = []
        
        connection = self.env['opencart.configuration']._create_connection()
        if connection[1]:
            url = connection[2]
            session = connection[0]
            session_key = connection[1]
            opncart_map_ids = self.env['opencart.product.category'].search([])
            if opncart_map_ids:
                for opncart_map_id in opncart_map_ids:
                    map_id.append(opncart_map_id.odoo_id.id)
            
            unmap_ids = self.env['product.category'].search([('id','not in', map_id)])
            if unmap_ids:
                for unmap_id in unmap_ids:
                    cat_id = self.sync_categories(session_key, session, url, unmap_id)
                    length.append(unmap_id.id)
            if len(length) > 0:
                text = "%s Odoo category ids has been Exported to OpenCart." % (
                    length)
            else:
                raise UserError(_("No new Category(s) found."))
            partial = self.env['wizard.message'].create({'text': text})
            return {'name': _("Information"),
                    'view_mode': 'form',
                    'view_id': False,
                    'view_type': 'form',
                    'res_model': 'wizard.message',
                    'res_id': partial.id,
                    'type': 'ir.actions.act_window',
                    'nodestroy': True,
                    'target': 'new',
                    'domain': '[]',
                    }

    @api.model
    def export_bulk_category(self):
        text = ''
        text1 = text2 = ''
        fail_ids = []
        error_ids = []
        up_error_ids = []
        success_up_ids = []
        success_exp_ids = []
        get_product_data = {}
        bulk_ids = self._context.get('active_ids')
        bulk_ids = self.env['product.category'].browse(bulk_ids)
        map_obj = self.env['opencart.product.category']
        connection = self.env[
            'opencart.configuration']._create_connection()
        if connection:
            url = connection[2]
            session = connection[0]
            session_key = connection[1]
            for l in bulk_ids:
                search = map_obj.search([('odoo_id', '=', l.id)])
                if not search:
                    cat_id = self.sync_categories(session_key, session, url, l.id)
                    if cat_id:
                        success_exp_ids.append(l.id)
                else:
                    # map_id = self.env[
                        # 'product.category'].browse(cr, uid, l)
                    if search.need_sync == 'yes':
                        cat_update = self._update_specific_category(l.id, session_key, session, url)
                        if cat_update[0] != 0:
                            success_up_ids.append(l.id)
                        else:
                            up_error_ids.append(cat_update[1])
                    else:
                        fail_ids.append(l.id)
            if success_exp_ids:
                text = "\nThe listed Category ids %s has been created on opencart." % (
                    success_exp_ids)
            if fail_ids:
                text += "\nSelected Category ids %s are already Synchronized on opencart." % (
                    fail_ids)
            if success_up_ids:
                text1 = '\nThe listed Category ids %s has been successfully updated to opencart. \n' % success_up_ids
            if up_error_ids:
                text2 = '\nThe Listed Category ids %s did not updated on opencart.' % up_error_ids
            partial = self.env['wizard.message'].create({'text': text + text1 + text2})
            return {'name': _("Information"),
                    'view_mode': 'form',
                    'view_id': False,
                    'view_type': 'form',
                    'res_model': 'wizard.message',
                    'res_id': partial.id,
                    'type': 'ir.actions.act_window',
                            'nodestroy': True,
                            'target': 'new',
                            'domain': '[]',
                    }

    @api.multi
    def update_products(self):
        text = text1 = ''
        up_error_ids = []
        success_ids = []
        connection = self.env['opencart.configuration']._create_connection()
        if connection:
            url = connection[2]
            session = connection[0]
            session_key = connection[1]
            pro_ids = self.env['opencart.product.template'].search([('need_sync', '=', 'yes')])
            if not pro_ids:
                raise UserError(_(
                    "No product(s) has been found to be Update on opencart!!!"))
            else:
                for i in pro_ids:
                    pro_update = self._update_specific_product(i.erp_template_id, i.oc_product_id, url, session, session_key)
                    if pro_update[0] != 0:
                        success_ids.append(i.erp_template_id)
                        i.write({'need_sync': 'no'})
                    else:
                        up_error_ids.append(pro_update[1])
                if success_ids:
                    text = 'The Listed Product ids %s has been sucessfully updated to opencart. \n' % success_ids
                if up_error_ids:
                    text1 = 'The Listed Product ids %s does not updated on opencart.' % up_error_ids
                text2 = text + text1
                if not text2:
                    raise UserError(_("No product(s) has been found to be Update on OpenCart!!!"))
                partial = self.env['wizard.message'].create({'text': text2})
                return {'name': _("Information"),
                        'view_mode': 'form',
                        'view_id': False,
                        'view_type': 'form',
                        'res_model': 'wizard.message',
                        'res_id': partial.id,
                        'type': 'ir.actions.act_window',
                                'nodestroy': True,
                                'target': 'new',
                                'domain': '[]',
                        }

    @api.multi
    def _update_specific_product(self, obj_pro, oc_pro_id, url, session, session_key):
        oc_categ_id = 0
        route = 'product'
        option_id = False
        status = False
        get_product_data = {}
        value_dict = {}
        oc_attr_value_ids = []
        option_val_obj = self.env['opencart.product.option.value']
        option_obj = self.env['opencart.product.option']
        if obj_pro:
            obj_pro = self.env['product.template'].browse(obj_pro)
            pro_id = obj_pro.id
            has_attributes = obj_pro.attribute_line_ids
            if len(has_attributes) > 1:
                raise UserError(_(
                    "Products with Multiple Attribute cannot be Exported!!! Product ID=%s") % (id))
            if 'choice' in self._context and self._context['choice'] == 'variant':
                if has_attributes:
                    option_name = has_attributes.attribute_id.name
                    erp_attr_id = has_attributes.attribute_id.id
                    attr_search = option_obj.search([('erp_id', '=', erp_attr_id)])
                    if attr_search:
                        option_id = attr_search[0].opencart_id
                        for k in obj_pro.product_variant_ids:
                            erp_product_id = k.id
                            qty = k.qty_available
                            price_extra = abs(k.price_extra)
                            if k.price_extra < 0:
                                price_prefix = '-'
                            else:
                                price_prefix = '+'
                            map_search = option_val_obj.search([('erp_id', '=', k.attribute_value_ids.id)])
                            if map_search:
                                option_val_id = map_search[0].opencart_value_id
                                value_dict = {
                                    'quantity': str(self.env['opencart.configuration'].get_quantity(k)),
                                    'price_prefix': price_prefix,
                                    'price': str(price_extra),
                                    'option_value_id': str(option_val_id),
                                    'erp_product_id': str(erp_product_id),
                                }
                                oc_attr_value_ids.append(value_dict)
                            else:
                                raise UserError(_(
                                    "Products Attributes Values have not been mapped. Please map the Odoo Attribute Values from OpenCart!!\n Odoo Attribute Values ID: %s") % (k.attribute_value_ids.id))
                    else:
                        raise UserError(_(
                            "Products Attributes have not been mapped. Please map the Odoo Attributes from OpenCart!!! \n Odoo Attribute ID: %s") % (erp_attr_id))
                    if option_id:
                        get_product_data['oc_option_name'] = option_name
                        get_product_data['oc_option_id'] = str(option_id)
                        get_product_data[
                            'oc_option_value_ids'] = oc_attr_value_ids
                else:
                    get_product_data['variant_id'] = str(
                        obj_pro.product_variant_ids.id)
        if pro_id and oc_pro_id:
            pro = 0
            oc_categ_id = 0
            prod_catg = []
            for j in obj_pro.categ_ids:
                oc_categ_id = self.sync_categories(session_key, session, url, j)
                prod_catg.append(oc_categ_id)
            if obj_pro.categ_id.id:
                oc_categ_id = self.sync_categories(session_key, session, url, obj_pro.categ_id)
                prod_catg.append(oc_categ_id)
            get_product_data['product_id'] = oc_pro_id
            get_product_data['name'] = obj_pro.name
            get_product_data['keyword'] = obj_pro.name
            get_product_data['description'] = obj_pro.description or ' '
            get_product_data['ean'] = obj_pro.barcode or ' '
            get_product_data['sku'] = obj_pro.default_code or 'Ref %s' % pro_id
            get_product_data['price'] = obj_pro.list_price or 0.00
            get_product_data['quantity'] = self.env['opencart.configuration'].get_quantity(obj_pro)
            get_product_data['product_category'] = list(set(prod_catg))
            get_product_data['erp_template_id'] = obj_pro.id
            get_product_data['erp_product_id'] = obj_pro.id
            get_product_data['session'] = session_key
            get_product_data['product_image'] = obj_pro.image
            if get_product_data['product_image']:
                get_product_data['product_image'] = get_product_data['product_image'].decode()
            # get_product_data['product_image'] = get_product_data['product_image'].decode()
            param = json.dumps(get_product_data)
            resp = session.get_session_key(url+route, param)
            # _logger.info('............ %r .............', resp.content)
            # _logger.info('..........data: %r ....................', param)
            resp = resp.json()
            key = str(resp[0])
            oc_id = resp[1]
            status = resp[2]
            if not status:
                return [0, str(pro_id) + str(key)]
            if status:
                for k in oc_id['merge_data']:
                    temp = {'product_name': k, 'erp_template_id': get_product_data[
                        'erp_template_id'], 'oc_product_id': oc_id['product_id'], 'oc_option_id': oc_id['merge_data'][k]}
                    search = self.env['opencart.product'].search([('product_name', '=', k)]).ids
                    if search and self._context['choice'] == 'variant':
                        search = self.env[
                            'opencart.product'].unlink(search)
                    self.env['opencart.product'].create(temp)
            return [1, oc_id]

    @api.multi
    def prodcreate(self, url, session, pro_id, put_product_data):
        route = 'product'
        pro = 0
        param = json.dumps(put_product_data)
        resp = session.get_session_key(url+route, param)
        resp = resp.json()
        key = str(resp[0])
        oc_id = resp[1]
        status = resp[2]
        if not status:
            return [0, str(pro_id) + str(key)]
        if status:
            pro = oc_id
            temp = {'template_name': put_product_data['erp_template_id'], 'erp_template_id': put_product_data[
                'erp_template_id'], 'oc_product_id': pro['product_id']}
            self.env['opencart.product.template'].create(temp)
            for k in pro['merge_data']:
                temp2 = {'product_name': k, 'erp_template_id': put_product_data[
                    'erp_template_id'], 'oc_product_id': pro['product_id'], 'oc_option_id': pro['merge_data'][k]}

                self.env['opencart.product'].create(temp2)
            return [1, pro['product_id']]

    @api.multi
    def _export_specific_product(self, obj_pro, url, session, session_key):
        """
        @param code: product Id.
        @param context: A standard dictionary
        @return: list
        """
        oc_categ_id = 0
        option_id = False
        product_data = {}
        value_dict = {}
        oc_attr_value_ids = []
        option_val_obj = self.env['opencart.product.option.value']
        option_obj = self.env['opencart.product.option']
        if obj_pro:
            obj_pro = self.env['product.template'].browse(obj_pro)
            has_attributes = obj_pro.attribute_line_ids
            if len(has_attributes) > 1:
                raise UserError(_("Products with Multiple Attribute cannot be Exported!!! Product ID=%s") % (obj_pro.id))
            if has_attributes:
                option_name = has_attributes.attribute_id.name
                erp_attr_id = has_attributes.attribute_id.id
                attr_search = option_obj.search([('erp_id', '=', erp_attr_id)])
                if attr_search:
                    option_id = attr_search[0].opencart_id
                    for k in obj_pro.product_variant_ids:
                        erp_product_id = k.id
                        qty = k.qty_available
                        price_extra = abs(k.price_extra)
                        if k.price_extra < 0:
                            price_prefix = '-'
                        else:
                            price_prefix = '+'
                        map_search = option_val_obj.search([('erp_id', '=', k.attribute_value_ids.id)])
                        if map_search:
                            option_val_id = map_search[0].opencart_value_id
                            value_dict = {
                                'quantity': str(self.env['opencart.configuration'].get_quantity(k)),
                                'price_prefix': price_prefix,
                                'price': str(price_extra),
                                'option_value_id': str(option_val_id),
                                'erp_product_id': str(erp_product_id),
                            }
                            oc_attr_value_ids.append(value_dict)
                        else:
                            raise UserError(_(
                                "Products Attributes Values have not been mapped. Please map the Odoo Attribute Values from OpenCart!!\n Odoo Attribute Values ID: %s") % (k.attribute_value_ids.id))
                else:
                    raise UserError(_(
                        "Products Attributes have not been mapped. Please map the Odoo Attributes from OpenCart!!! \n Odoo Attribute ID: %s") % (erp_attr_id))
                if option_id:
                    product_data['oc_option_name'] = option_name
                    product_data['oc_option_id'] = str(option_id)
                    product_data['oc_option_value_ids'] = oc_attr_value_ids
            else:
                product_data['variant_id'] = str(
                    obj_pro.product_variant_ids.id)

            oc_categ_id = 0
            prod_catg = []
            for j in obj_pro.categ_ids:
                oc_categ_id = self.sync_categories(session_key, session, url, j)
                prod_catg.append(oc_categ_id)
            if obj_pro.categ_id.id:
                oc_categ_id = self.sync_categories(session_key, session, url, obj_pro.categ_id)
                prod_catg.append(oc_categ_id)
            product_data['sku'] = obj_pro.default_code or 'Ref Odoo %s' % obj_pro.id
            product_data['model'] = obj_pro.default_code or 'Ref Odoo %s' % obj_pro.id
            product_data['name'] = obj_pro.name
            product_data['keyword'] = obj_pro.name
            product_data['description'] = obj_pro.description or ' '
            product_data['ean'] = obj_pro.barcode or ' '
            product_data['price'] = obj_pro.list_price or 0.00
            product_data['quantity'] = self.env['opencart.configuration'].get_quantity(obj_pro)
            product_data['weight'] = obj_pro.weight or 0.00
            product_data['erp_product_id'] = obj_pro.id
            product_data['product_category'] = list(set(prod_catg))
            product_data['erp_template_id'] = obj_pro.id
            product_data['product_image'] = obj_pro.image
            product_data['minimum'] = '1'
            product_data['subtract'] = '1'
            if product_data['product_image']:
                product_data['product_image'] = product_data['product_image'].decode()
            product_data['session'] = session_key
            pro = self.prodcreate(url, session, obj_pro, product_data)
            return pro

    @api.multi
    def export_products(self):
        error_ids = []
        success_ids = []
        text = text1 = ''
        map = []
        connection = self.env['opencart.configuration']._create_connection()
        if connection:
            url = connection[2]
            session = connection[0]
            session_key = connection[1]
            prod_obj = self.env['product.template']
            already_mapped = self.env[
                'opencart.product.template'].search([])
            for m in already_mapped:
                # map_obj = self.pool.get(
                #     'opencart.product.template').browse(cr, uid, m)
                map.append(m.erp_template_id)
            need_to_export = prod_obj.search([('id', 'not in', map), ('type', 'not in', ['service'])]).ids
            if need_to_export:
                for k in need_to_export:
                    pro = self._export_specific_product(k, url, session, session_key)
                if pro[0] != 0:
                    success_ids.append(k)
                else:
                    error_ids.append(pro[1])
            else:
                raise UserError(_(
                    "No new product(s) found."))
            if success_ids:
                text = 'The Listed Product ids %s has been successfully Exported to OpenCart. \n' % success_ids
            if error_ids:
                text1 = 'The Listed Product ids %s Reference(SKU) already exists on opencart.' % error_ids
            partial = self.env['wizard.message'].create({'text': text + text1})
            return {'name': _("Information"),
                    'view_mode': 'form',
                    'view_id': False,
                    'view_type': 'form',
                    'res_model': 'wizard.message',
                    'res_id': partial.id,
                    'type': 'ir.actions.act_window',
                    'nodestroy': True,
                    'target': 'new',
                    'domain': '[]',
                    }

    @api.model
    def export_bulk_product(self):
        error_ids = []
        text1 = text2 = message = ''
        up_error_ids = []
        success_up_ids = []
        success_exp_ids = []
        exported = 0
        updated = 0
        selected_ids = self._context.get('active_ids')
        map_obj = self.env['product.template']
        connection = self.env['opencart.configuration']._create_connection()
        if connection:
            url = connection[2]
            session = connection[0]
            session_key = connection[1]
            for j in selected_ids:
                check = self.env['opencart.product.template'].search([('erp_template_id', '=', j)])
                if not check:
                    pro = self._export_specific_product(j, url, session, session_key)
                    if pro[0] != 0:
                        success_exp_ids.append(j)
                        exported = exported + 1
                    else:
                        error_ids.append(pro[1])
                check_update = self.env['opencart.product.template'].search([('erp_template_id', '=', j), ('need_sync', '=', 'yes')])
                if check_update:
                    oc_product_id = check_update[0].oc_product_id
                    pro_update = self._update_specific_product(j, oc_product_id, url, session, session_key)
                    if pro_update[0] != 0:
                        success_up_ids.append(j)
                        updated = updated + 1
                    else:
                        up_error_ids.append(pro_update[1])
            if exported == updated == 0:
                message = message + \
                    "Selected product(s) already Exported to OpenCart. No need to Update either!!"
            else:
                if exported > 0:
                    text1 = "Product ids %s has been exported to OpenCart." % (
                        success_exp_ids)
                if updated > 0:
                    text1 = '\nProduct ids %s has been successfully updated to OpenCart. \n' % success_up_ids
                message = message + text1 + text2

            partial = self.env['wizard.message'].create({'text': message})
            return {'name': _("Information"),
                    'view_mode': 'form',
                    'view_id': False,
                    'view_type': 'form',
                    'res_model': 'wizard.message',
                    'res_id': partial.id,
                    'type': 'ir.actions.act_window',
                            'nodestroy': True,
                            'target': 'new',
                            'domain': '[]',
                    }


class opencart_product(models.Model):
    _name = "opencart.product"
    _description = "Opencart Product Mapping"
    _order = "need_sync"

    @api.multi
    def _is_active(self, name, arg):
        res = {}
        prod_obj = self.env['product.product']
        for id in self._ids:
            res[id] = {}.fromkeys(name, False)
        for i in self._ids:
            map_obj = self.env[
                'prestashop.openerp.mapping'].browse(i)
            obj = sale_obj.browse(map_obj.erp_id)

        return res

    name = fields.Char('Product Name', size=100)
    product_name = fields.Many2one('product.product', 'Product Name')
    erp_template_id = fields.Integer('Odoo`s Template Id')
    oc_product_id = fields.Integer('OpenCart`s Product Id')
    oc_option_id = fields.Integer('OpenCart`s Option Id', default=0)
    need_sync = fields.Selection((('yes', 'Yes'), ('no', 'No')), 'Update Required', default='no')
    active = fields.Boolean(related='product_name.active', type="boolean", string="Active")
    instance_id = fields.Many2one('opencart.configuration', 'Instance Id', default = lambda self: self.env['opencart.configuration'].search([('active','=',True)],limit=1).id or False)


class opencart_product_category(models.Model):
    _name = 'opencart.product.category'

    ecommerce_cat_id = fields.Integer('Opencart Category Id')
    odoo_id = fields.Many2one('product.category','Erp Product Category')
    need_sync = fields.Selection((('yes', 'Yes'), ('no', 'No')), 'Update Required', default='no')
    created_by = fields.Char('Created By', default = 'Odoo')
    instance_id = fields.Many2one('opencart.configuration', 'Instance Id', default = lambda self: self.env['opencart.configuration'].search([('active','=',True)],limit=1).id or False)




class opencart_product_template(models.Model):
    _name = "opencart.product.template"
    _description = "Opencart Template Mapping"
    _order = "need_sync"

    name = fields.Char('Product Name', size=100)
    template_name = fields.Many2one('product.template', 'Template Name')
    erp_template_id = fields.Integer('Odoo`s Template Id')
    oc_product_id = fields.Integer('OpenCart`s Product Id')
    need_sync = fields.Selection((('yes', 'Yes'), ('no', 'No')), 'Update Required', default='no')
    instance_id = fields.Many2one('opencart.configuration', 'Instance Id', default = lambda self: self.env['opencart.configuration'].search([('active','=',True)],limit=1).id or False)


class opencart_product_option(models.Model):
    _name = "opencart.product.option"
    _description = "Opencart Options Mapping"
    _order = 'need_sync'

    name = fields.Many2one('product.attribute', 'Product Options')
    erp_id = fields.Integer('Odoo`s Attribute Id')
    opencart_id = fields.Integer('OpenCart`s Option Id')
    need_sync = fields.Selection((('yes', 'Yes'), ('no', 'No')), 'Update Required', default='no')
    instance_id = fields.Many2one('opencart.configuration', 'Instance Id', default = lambda self: self.env['opencart.configuration'].search([('active','=',True)],limit=1).id or False)


class opencart_product_option_value(models.Model):
    _name = "opencart.product.option.value"
    _description = "Opencart Value Mapping"
    _order = 'need_sync'

    name = fields.Many2one('product.attribute.value', 'Product Option Value')
    erp_id = fields.Integer('Odoo`s Attribute Value Id')
    opencart_value_id = fields.Integer('Opencart`s`s Option Value Id')
    erp_attr_id = fields.Integer('Odoo`s Attribute Id')
    opencart_option_id = fields.Integer('Opencart`s Option Id')
    need_sync = fields.Selection((('yes', 'Yes'), ('no', 'No')), 'Update Required', default='no')
    instance_id = fields.Many2one('opencart.configuration', 'Instance Id', default = lambda self: self.env['opencart.configuration'].search([('active','=',True)],limit=1).id or False)


class product_product(models.Model):
    _inherit = 'product.product'

    @api.multi
    def check_for_new_price(self, template_id, value_id, price_extra):
        product_attribute_price = self.env['product.attribute.price']
        exists = product_attribute_price.search([('product_tmpl_id', '=', template_id), ('value_id', '=', value_id)])
        _logger.info("webkul testing %r %r", template_id, value_id)
        if not exists:
            temp = {'product_tmpl_id': template_id,
                    'value_id': value_id, 'price_extra': price_extra}
            pal_id = product_attribute_price.create(temp)
            return True
        else:
            pal_id = exists[0]
            pal_id.write({'price_extra': price_extra})
            return True

    @api.multi
    def check_for_new_attrs(self, template_id, ps_attributes):
        product_template=self.env['product.template']
        product_attribute_line=self.env['product.template.attribute.line']
        all_values = []
        for attribute_id in ps_attributes:
            exists = product_attribute_line.search([('product_tmpl_id','=',template_id),('attribute_id','=',int(attribute_id))])
            if not exists:
                temp ={'product_tmpl_id':template_id,'attribute_id':attribute_id,'value_ids':[[4,int(ps_attributes[attribute_id][0])]]}
                pal_id = product_attribute_line.create(temp)
            else:
                pal_id = exists[0]
                pal_id.write({'value_ids':[[4,int(ps_attributes[attribute_id][0])]]})
            all_values.append(int(ps_attributes[attribute_id][0]))
        return [[6,0,all_values]]


    @api.model
    def create(self, vals):
        if 'oc_variant' in self._context:
            template_obj = self.env['product.template'].browse(vals['product_tmpl_id'])
            vals['name'] = template_obj.name
            vals['description'] = template_obj.description
            vals['description_sale'] = template_obj.description_sale
            vals['type'] = template_obj.type
            vals['categ_id'] = template_obj.categ_id.id
            vals['uom_id'] = template_obj.uom_id.id
            vals['uom_po_id'] = template_obj.uom_po_id.id
            vals['default_code'] = _unescape(vals['default_code'])
            if 'oc_attributes' in vals:
                vals['attribute_value_ids'] = self.check_for_new_attrs(template_obj.id, vals['oc_attributes'])
        erp_id = super(product_product, self).create(vals)
        if 'oc_variant' in self._context:
            opencart_product = self.env['opencart.product']
            exists = opencart_product.search([('erp_template_id', '=', vals[
                                             'product_tmpl_id']), ('oc_option_id', '=', 0)])
            if exists:
                pp_map = opencart_product.browse(exists[0].id)
                if pp_map.product_name:
                    pp_map.product_name.with_context({}).write({'active':False})
                exists.unlink()
            opencart_product.create({
                'product_name': erp_id.id,
                'erp_template_id': template_obj.id,
                'oc_product_id': self._context['opencart_id'],
                'oc_option_id': self._context['oc_option_id']
            })
        return erp_id

    @api.multi
    def write(self, vals):
        if 'opencart_variant' in self._context:
            template_obj = self.env['product.template'].browse(vals['product_tmpl_id'])
            vals['name'] = template_obj.name
            vals['description'] = template_obj.description
            vals['description_sale'] = template_obj.description_sale
            vals['type'] = template_obj.type
            vals['categ_id'] = template_obj.categ_id.id
            vals['uom_id'] = template_obj.uom_id.id
            vals['uom_po_id'] = template_obj.uom_po_id.id
            vals['default_code'] = _unescape(vals['default_code'])
        if 'extra_price' in self._context:
            self.check_for_new_price(vals['product_tmpl_id'], self._context[
                                     'attr_value_id'], self._context['extra_price'])
        return super(product_product, self).write(vals)



class product_template(models.Model):
    _inherit = 'product.template'


    @api.model
    def create_product_template_dict(self, vals):
        template_id=self.create(vals)
        variant_ids_ids =template_id.product_variant_ids
        temp = {'template_id': template_id.id}
        if len(variant_ids_ids) == 1:
            temp['product_id'] = variant_ids_ids[0].id
        else:
            temp['product_id'] = -1
        self.env['opencart.product.template'].create({
            'template_name': template_id.id,
            'erp_template_id': template_id.id,
            'oc_product_id': self._context['opencart_id']
        })
        self.env['opencart.product'].create({
            'product_name': temp['product_id'],
            'erp_template_id': template_id.id,
            'oc_product_id': self._context['opencart_id']
        })
        return temp


    @api.model
    def create(self, vals):
        if 'opencart' in self._context:
            if 'name' in vals:
                vals['name'] = _unescape(vals['name'])
            if 'description' in vals:
                vals['description'] = _unescape(vals['description'])
                vals['description_sale'] = _unescape(vals['description'])
                #_logger.info('.............. Vals : %r ............', vals['description_sale'])
        template_id = super(product_template, self).create(vals)
        return template_id

    @api.multi
    def write(self, vals):
        map_obj = self.env['opencart.product.template']
        if 'opencart' not in self._context:
            if self._ids:
                if type(self._ids) == list:
                    erp_id = self._ids[0]
                else:
                    erp_id = self._ids
                map_ids = map_obj.sudo().search([('template_name', 'in', erp_id)])
                if map_ids:
                    map_ids[0].sudo().write({'need_sync': 'yes'})
        if 'opencart' in self._context:
            if 'name' in vals:
                vals['name'] = _unescape(vals['name'])
            if 'description' in vals:
                vals['description'] = _unescape(vals['description'])
                vals['description_sale'] = _unescape(vals['description'])
                #_logger.info('.............. Vals : %r ............', vals['description_sale'])
        return super(product_template, self).write(vals)

    categ_ids = fields.Many2many('product.category', 'mulit_categ1', 'mulit_categ2', 'mulit_categ3', 'Product Categories')
# END
