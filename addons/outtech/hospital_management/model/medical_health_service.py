# -*- coding: utf-8 -*-
##############################################################################
#
#    This module uses OpenERP, Open Source Management Solution Framework.
#    Copyright (C) 2014-Today BrowseInfo (<http://www.browseinfo.in>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################
from openerp import api, fields, models, _
from datetime import date


class medical_health_services_invoice(models.Model):
    
    _name = 'medical.health.service.invoice'
    
    def create_medical_service_invoice(self, cr, uid, id, context = None):
        if context == None:
            context = {}
        active_id = context.get('active_id')
        lab_req_obj = self.pool.get('medical.health_service')
        account_invoice_obj  = self.pool.get('account.invoice')
        account_invoice_line_obj = self.pool.get('account.invoice.line')
        lab_req = lab_req_obj.browse(cr, uid, active_id, context = context)
        if lab_req.is_invoiced == True:
            raise UserError(_('Invoice is Already Exist'))        
        
        res = account_invoice_obj.create(cr, uid, {'partner_id': lab_req.patient_id.patient_id.id,
                                                   'date_invoice': date.today(),
                                             'account_id':lab_req.patient_id.patient_id.property_account_receivable_id.id,
                                             }, context = context)
        for p_line in lab_req.service_line_ids:
            if p_line.to_invoice == True:
                
                res1 = account_invoice_line_obj.create(cr, uid, {'product_id':p_line.product_id.id ,
                                             'product_uom': p_line.product_id.uom_id.id,
                                             'name': p_line.product_id.name,
                                             'product_uom_qty':1,
                                             'price_unit':p_line.product_id.lst_price, 
                                             'account_id': lab_req.patient_id.patient_id.property_account_receivable_id.id,
                                             'invoice_id': res}, 
                                            context = context)
        if res:
            
            lab_req_obj.write(cr , uid ,active_id,{'is_invoiced': True}, context = context)
            imd = self.pool.get('ir.model.data')
            action = imd.xmlid_to_object(cr, uid,'account.action_invoice_tree1')
            list_view_id = imd.xmlid_to_res_id(cr, uid,'account.view_order_form')
            result = {
                                'name': action.name,
                                'help': action.help,
                                'type': action.type,
                                'views': [ [list_view_id,'form' ]],
                                'target': action.target,
                                'context': action.context,
                                'res_model': action.res_model,
                                'res_id':res,
                            }
            if res:
                    result['domain'] = "[('id','=',%s)]" % res
                    
        return result  
    

class medical_health_service(models.Model):
    _name = "medical.health_service"

    name = fields.Char('ID')
    is_invoiced =  fields.Boolean(default = False)
    desc = fields.Char(string="Description", required=True)
    patient_id = fields.Many2one('medical.patient','Patient', required=True)
    service_date = fields.Date('Date')
    description = fields.Char('Description')
    service_line_ids = fields.One2many('medical.health_service.line','health_service_id','Service line')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('medical_health_ser') 
        result = super(medical_health_service, self).create(vals)
        return result

    @api.multi
    def button_set_to_confirm(self):
        self.write({'state':'confirmed'})

class medical_health_service_line(models.Model):
    _name = "medical.health_service.line"

    health_service_id = fields.Many2one('medical.health_service')
    to_invoice = fields.Boolean('Invoice', default =True)
    desc = fields.Char('Description')
    product_id = fields.Many2one('product.product','Product')
    qty = fields.Integer('Qty')
    from_date = fields.Date('From')
    to_date = fields.Date('To')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: