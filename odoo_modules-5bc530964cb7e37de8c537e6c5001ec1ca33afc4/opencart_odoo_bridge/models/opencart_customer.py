from  odoo import models,fields,api


class opencart_customer(models.Model):
    _name = 'opencart.customer'

    odoo_id = fields.Many2one('res.partner' ,'Odoo Customer Id')
    ecommerce_customer_id = fields.Integer('Ecommerce Customer Id')
    ecommerce_address_id = fields.Integer('Ecommerce Address Id', default=0)
    need_sync = fields.Selection((('yes', 'Yes'), ('no', 'No')), 'Update Required', default='no')
    created_by = fields.Char('Created By', default = "Odoo")
    instance_id = fields.Many2one('opencart.configuration', 'Instance Id', default = lambda self: self.env['opencart.configuration'].search([('active','=',True)],limit=1).id or False)