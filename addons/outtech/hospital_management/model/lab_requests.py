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
from odoo import api, fields, models, _
from datetime import date
from odoo.exceptions import Warning


# classes under  menu of laboratry

class medical_lab_test_create(models.Model):
    _name = 'medical.lab.test.create'

    @api.multi
    def create_lab_test(self):
        print "==========abc"
        res_ids = []
        lab_rqu_obj = self.env['medical.patient.lab.test']
        print  "get active ids======================", self._context.get('active_ids')
        browse_records = lab_rqu_obj.browse(self._context.get('active_ids'))
        result = {}
        for browse_record in browse_records:
            medical_lab_obj = self.env['medical.lab']
            print "===============browse_record.doctor_id.id", browse_record.doctor_id.id, browse_record
            res = medical_lab_obj.create({'name': self.env['ir.sequence'].next_by_code('ltest_seq'),
                                          'patient_id': browse_record.patient_id.id or False,
                                          'date_requested': browse_record.date or False,
                                          'test_id': browse_record.name.id or False,
                                          'requestor_id': browse_record.doctor_id.id or False,
                                          })
            res_ids.append(res.id)
            if res_ids:
                imd = self.env['ir.model.data']
                write_ids = lab_rqu_obj.browse(self._context.get('active_id'))
                write_ids.write({'state': 'tested'})
                action = imd.xmlid_to_object('hospital_management.action_view_lab_results_tree')
                list_view_id = imd.xmlid_to_res_id('hospital_management.view_medical_lab')
                form_view_id = imd.xmlid_to_res_id('hospital_management.view_medical_lab_form')
                result = {
                    'name': action.name,
                    'help': action.help,
                    'type': action.type,
                    'views': [[list_view_id, 'tree'], [form_view_id, 'form']],
                    'target': action.target,
                    'context': action.context,
                    'res_model': action.res_model,
                    'res_id': res.id,

                }
            if res_ids:
                result['domain'] = "[('id','=',%s)]" % res_ids

        return result


class medical_lab_test_create(models.Model):
    _name = 'medical.lab.test.invoice'

    @api.multi
    def create_lab_invoice(self):
        if self._context == None:
            self._context = {}
        active_ids = self._context.get('active_ids')
        list_of_ids = []
        lab_req_obj = self.env['medical.patient.lab.test']
        sale_order_obj = self.env['sale.order']
        account_invoice_obj = self.env['account.invoice']
        account_invoice_line_obj = self.env['account.invoice.line']
        for active_id in active_ids:
            lab_req = lab_req_obj.browse(active_id)
            if lab_req.is_invoied == True:
                raise Warning('All ready Invoiced.')
            res = account_invoice_obj.create(
                {'partner_id': lab_req.patient_id.patient_id.id,
                 'date_invoice': date.today(),
                 'account_id': lab_req.patient_id.patient_id.property_account_receivable_id.id,
                 })

            res1 = account_invoice_line_obj.create({
                'product_id': lab_req.name.service.id,
                'product_uom': lab_req.name.service.uom_id.id,
                'name': lab_req.name.service.name,
                'product_uom_qty': 1,
                'price_unit': lab_req.name.service.lst_price,
                'account_id': lab_req.patient_id.patient_id.property_account_receivable_id.id,
                'invoice_id': res.id})
            list_of_ids.append(res.id)
        if list_of_ids:
            imd = self.env['ir.model.data']
            write_ids = lab_req_obj.browse(self._context.get('active_id'))
            write_ids.write({'is_invoied': True})
            action = imd.xmlid_to_object('account.action_invoice_tree1')
            list_view_id = imd.xmlid_to_res_id('account.invoice.supplier.tree')
            form_view_id = imd.xmlid_to_res_id('account.invoice.supplier.form')
            result = {
                'name': action.name,
                'help': action.help,
                'type': action.type,
                'views': [[list_view_id, 'tree'], [form_view_id, 'form']],
                'target': action.target,
                'context': action.context,
                'res_model': action.res_model,

            }
            if list_of_ids:
                result['domain'] = "[('id','=',%s)]" % list_of_ids

        return result


class MedicalPatientLabTest(models.Model):
    _name = 'medical.patient.lab.test'
    # ORM FIELDS
    medical_inpatient_registration_id = fields.Many2one(
        'medical.inpatient.registration',
        string=_("Inpatiente Registration"), required=True
    )
    request = fields.Char(
        string=_("Request"), readonly=True
    )
    date = fields.Datetime(
        string=_("Date"), default=fields.Date.context_today
    )
    owner_name = fields.Many2one(
        'res.partner', string=_("Owner Name")
    )
    urgent = fields.Boolean(
        string=_("Urgent")
    )
    owner_id = fields.Many2one(
        'res.partner'
    )
    state = fields.Selection([('draft', 'Draft'), ('tested', 'Tested'), ('cancel', 'Cancel')], readonly=True,
                             default='draft')
    name = fields.Many2one(
        'medical.test_type',
        string=_("Test Type"), required=True
    )
    patient_id = fields.Many2one(
        'medical.patient',
        string=_("Patient")
    )
    doctor_id = fields.Many2one(
        'medical.physician',
        string=_("Doctor")
    )
    insurer_id = fields.Many2one(
        'medical.insurance',
        string=_("Insurer")
    )
    invoice_to_insurer = fields.Boolean(
        string=_("Invoice to Insurance")
    )
    lab_res_created = fields.Boolean(
        default=False
    )
    is_invoied = fields.Boolean(
        default=False
    )


    @api.model
    def create(self, vals):
        vals['request'] = self.env['ir.sequence'].next_by_code('test_seq')
        result = super(MedicalPatientLabTest, self).create(vals)
        return result

    def create_lab_test(self, cr, uid, ids, context=None):
        res_ids = []
        for id in ids:
            browse_record = self.browse(cr, uid, id, context=context)
            result = {}
            medical_lab_obj = self.pool.get('medical.lab')
            res = medical_lab_obj.create(cr, uid, {
                'name': self.pool.get('ir.sequence').next_by_code(cr, uid, 'ltest_seq'),
                'patient_id': browse_record.patient_id.id,
                'date_requested': browse_record.date or False,
                'test_id': browse_record.name.id or False,
                'requestor_id': browse_record.doctor_id.id or False,
            })
            res_ids.append(res)
            if res_ids:
                imd = self.pool.get('ir.model.data')
                action = imd.xmlid_to_object(cr, uid, 'hospital_management.action_view_lab_results1')
                list_view_id = imd.xmlid_to_res_id(cr, uid, 'hospital_management.view_medical_lab_form')
                form_view_id = imd.xmlid_to_res_id(cr, uid, 'hospital_management.view_medical_lab_form')
                result = {
                    'name': action.name,
                    'help': action.help,
                    'type': action.type,
                    'views': [[list_view_id, 'tree'], [form_view_id, 'form']],
                    'target': action.target,
                    'context': action.context,
                    'res_model': action.res_model,
                    'res_id': res,

                }

            if res_ids:
                result['domain'] = "[('id','=',%s)]" % res_ids

        return result

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
