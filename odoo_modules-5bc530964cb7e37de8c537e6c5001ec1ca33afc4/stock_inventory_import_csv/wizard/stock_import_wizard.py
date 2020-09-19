# -*- coding:utf-8 -*-
import io
import base64
from odoo.tools import pycompat
from tempfile import TemporaryFile
from openerp import models, fields, api, _
import csv 
from openerp.exceptions import ValidationError

class ImportStockInventory(models.TransientModel):
    _name = 'import.stock.inventory'

    import_file = fields.Binary(string="Import Excel File", redonly=True)
    datas_fname = fields.Char('Import File')
    location_id = fields.Many2one('stock.location', 'Location', required=True)
    
    import_product_by = fields.Selection(
        [('name','Name'),
         ('code','Code'),
         ('barcode','Barcode')],
        string='Import Product By',
        default='name',
    )

    @api.multi
    def action_import_file(self):
        active_id = self._context.get('active_id')
        active_model = self._context.get('active_model')
        stock_id = self.env[active_model].browse(active_id)
        product_obj = self.env['product.product']
        product_uom_obj = self.env['uom.uom']
        stock_inv_line_obj = self.env['stock.inventory.line']
        prod_lot_obj = self.env['stock.production.lot']
        ctx = self.env.context
        if self.location_id:
            location_id = self.location_id.id
        elif 'active_id' in ctx:
            inventory_obj = self.env['stock.inventory']
            inventory = inventory_obj.browse(ctx['active_id'])
            location_id = inventory.location_id and inventory.location_id.id or False


        if self.datas_fname[-4:] == '.csv':
#             fileobj = TemporaryFile('w+')

            csv_data = base64.decodestring(self.import_file)
            csv_iterator = pycompat.csv_reader(
                io.BytesIO(csv_data),
                quotechar='"',
                delimiter=','
            )
            fields = next(csv_iterator)

            count = 1
            lines = []
            missing_product = []
            for row in csv_iterator:
#                 if count == 1:
#                     count += 1
#                     continue
#                 count += 1
                line_vals = {}
                lot_id = False
                try:
                    if row[3]:
                        lot_id = True
                except:
                    pass
                
                if lot_id:
                    prod_lot_id = prod_lot_obj.search([('name', '=', row[3])], limit=1)
                
                    if not prod_lot_id:
                          raise ValidationError(_('Below Serial Number is missing in system: %s.'%row[3]))
                    else:
                          line_vals.update({'prod_lot_id': prod_lot_id.id,})

#                product = product_obj.search([('default_code','=',row[0])])
                
                product_name = row[0]
#                product_name = sheet.cell(row,0).value
               
                print("==============>>>>",product_name)
                if self.import_product_by == 'name' and product_name:
                    productID = self.env['product.product'].search([('name','=',product_name)], limit=1)
                elif self.import_product_by == 'code' and product_name:
                    productID = self.env['product.product'].search([('default_code','=',product_name)], limit=1)
                elif self.import_product_by == 'barcode' and product_name:
                    productID = self.env['product.product'].search([('barcode','=',product_name)], limit=1)
                    print("=========productID=====>>>>",productID)
                    
                if len(row) == 6:
                    if row[4]:
                        pack_id = self.env['stock.quant.package'].search([('name','=',row[4])])
                        line_vals.update({
                             'package_id' : pack_id.id,
                        })
                        
                    if row[5]:
                        partner_id = self.env['res.partner'].search([('name','=',row[5])])
                        line_vals.update({
                              'partner_id' : partner_id.id,
                        })
                
                
                
                
                if product_name:
                    line_vals.update({
                            'product_id':productID.id,
                            'product_qty':row[1],
                            'inventory_id':stock_id.id,
                            'location_id': location_id,
                           
                        })
                    if row[1]:
                        uom = product_uom_obj.search([('name','=',row[2])])
                        if uom:
                            line_vals.update({'product_uom_id':uom.id})
                    lines.append(line_vals)
                else:
                    missing_product.append(row[0])
            if not missing_product and lines:
                for line_vals in lines:
                    stock_line = stock_inv_line_obj.create(line_vals)
            else:
                missing_product_name = ',\n'.join(missing_product)
                raise ValidationError(_('Below products are missing in system \n %s.'%missing_product_name))
        else:
            raise ValidationError(_('Wrong file format. Please enter .csv file.'))
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
