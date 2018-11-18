# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 BrowseInfo (<http://Browseinfo.in>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import api, fields, models, _
from datetime import datetime
from openerp.exceptions import UserError


class wizard_multiple_test_request(models.Model):

    _name = 'wizard.multiple.test.request'
    
    r_date = fields.Datetime('Request Date', required = True)
    patient_id =  fields.Many2one('medical.patient','Patient', required = True)
    urgent =  fields.Boolean('Urgent',)
    phy_id = fields.Many2one('medical.physician','Doctor', required = True)
    owner_id  = fields.Many2one('res.partner','Owner')
    tests_ids = fields.Many2many('medical.test_type', 
            'lab_test_report_test_rel', 'test_id', 'report_id', 'Tests')
       
       
    #@api.onchange('patient_id')
    #def on_change_patient_id(self):   
    #    self.owner_id = self.patient_id.patient_id.owner_id
         
    def create_lab_test(self, cr, uid, id , context = None):
        
        if context:
            context  = {}
        
        
        wizard_obj = self.browse(cr, uid, id, context = context)
#         if wizard_obj.patient_id != wizard_obj.patient_id.patient_id:
#              raise osv.except_osv(_('Warning!'),_('Please select correct owner.'))
        patient_id = wizard_obj.patient_id
        #owner_name = wizard_obj.owner_id
        phy_id = wizard_obj.phy_id
        #owner_id = wizard_obj.owner_id.id
        new_created_id_list  = []
        date = wizard_obj.r_date 
        for test_id in wizard_obj.tests_ids:
            lab_test_req_obj = self.pool.get('medical.test_type')
            test_browse_record = lab_test_req_obj.browse(cr, uid, test_id.id, context = context)
            test_name = test_browse_record.name
            medical_test_request_obj  = self.pool.get('medical.patient.lab.test')
            new_created_id = medical_test_request_obj.create( cr, uid, {'date': date,
                                                        'doctor_id': phy_id.id,
                                                        'patient_id':patient_id.id,
                                                        'state': 'tested',
                                                        #'owner_id': owner_id,
                                                        'name':test_id.id,
                                                        
                                                        'request' :self.pool.get('ir.sequence').next_by_code(cr, uid, 'test_seq')
      })
            
            
            
            new_created_id_list.append(new_created_id)
        if new_created_id_list:                     
            imd = self.pool.get('ir.model.data')
            action = imd.xmlid_to_object(cr, uid, 'hospital_management.action_tree_view_lab_requests', context = context)
            list_view_id = imd.xmlid_to_res_id(cr, uid, 'hospital_management.view_medical_tree_lab_req')

            result = {
                                'name': action.name,
                                'help': action.help,
                                'type': action.type,
                                'views': [ [list_view_id,'tree' ]],
                                'target': action.target,
                                'context': action.context,
                                'res_model': action.res_model,
                            }
            
            if len(new_created_id_list)  :
                        result['domain'] = "[('id','in',%s)]" % new_created_id_list
            return result

   
             
        
            

    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:    