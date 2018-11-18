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

class imaging_request(models.TransientModel):
    _name = "medical.imaging.test.request.wizard"

    phy_id = fields.Many2one('medical.physician',string="Name Of Physician", required = True)
    patient_id = fields.Many2one('medical.patient',string="Patient", required = True)
    test_date = fields.Date('Test Date', required = True)
    urgent = fields.Boolean('Urgent')
    test_ids = fields.Many2many('medical.imaging.test','img_test_report_test_rel', 'test_id', 'imag_id','Test')



    def create_lab_imaging_request(self,cr, uid, id, context = None):
        if context:
            context  = {}

        wizard_obj = self.browse(cr, uid, id, context = context)
        patient_id = wizard_obj.patient_id
        phy_id = wizard_obj.phy_id
        urgent = wizard_obj.urgent
        new_created_id_list  = []
        date = wizard_obj.test_date
        for test_id in wizard_obj.test_ids:
            imag_test_req_obj = self.pool.get('medical.imaging.test.request')
            new_created_id = imag_test_req_obj.create(cr, uid, {'test_date': date,
                                                        'request_id': phy_id.id,
                                                        'physician_id':phy_id.id,
                                                        'patient_id':patient_id.id,
                                                        'state': 'draft',
                                                        'urgent':urgent,
                                                        'test_id':test_id.id,
                                                        'name':self.pool.get('ir.sequence').next_by_code(cr, uid, 'imaging_seq')
      })


            new_created_id_list.append(new_created_id)
        if new_created_id_list:
            imd = self.pool.get('ir.model.data')
            action = imd.xmlid_to_object(cr, uid, 'health_care.action_medical_imaging_test_result_draft', context = context)
            print  "action=======",action
            list_view_id = imd.xmlid_to_res_id(cr, uid, 'health_care.medical_imaging_test_request_tree')

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



class medical_imaging_test_type(models.Model):
    _name = 'medical.imaging.test.type'

    name = fields.Char('Name', required = True)
    code = fields.Char('Code', required = True)

class medical_imaging_test(models.Model):
    _name = 'medical.imaging.test'

    name = fields.Char('Name', required = True)
    code = fields.Char('Code', required = True)
    product_id = fields.Many2one('product.product','Service', required = True)
    test_type_id = fields.Many2one('medical.imaging.test.type','Type', required = True)



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: