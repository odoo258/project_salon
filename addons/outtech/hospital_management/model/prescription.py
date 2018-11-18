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
from datetime import datetime, timedelta
from odoo import api, fields, models, _
from datetime import date
from odoo.exceptions import Warning
from odoo.exceptions import UserError


class create_prescription_invoice(models.TransientModel):
    _name = 'create.prescription.invoice'

    @api.multi
    def create_prescription_invoice(self):
        if self._context == None:
            context = {}
        active_ids = self._context.get('active_ids')
        active_ids = active_ids or False
        lab_req_obj = self.env['medical.prescription.order']
        account_invoice_obj = self.env['account.invoice']
        account_invoice_line_obj = self.env['account.invoice.line']
        inv_list = []
        lab_reqs = lab_req_obj.browse(active_ids, )
        for lab_req in lab_reqs:

            if len(lab_req.prescription_line_ids) < 1:
                raise Warning('At least one prescription line is required.')

            if lab_req.is_invoiced == True:
                raise Warning('All ready Invoiced.')
            res = account_invoice_obj.create({'partner_id': lab_req.patient_id.patient_id.id,
                                              'date_invoice': date.today(),
                                              'account_id': lab_req.patient_id.patient_id.property_account_receivable_id.id,
                                              }, )
            for p_line in lab_req.prescription_line_ids:
                res1 = account_invoice_line_obj.create({'product_id': p_line.medicament_id.product_id.id,
                                                        'product_uom_id': p_line.medicament_id.product_id.uom_id.id,
                                                        'name': p_line.medicament_id.product_id.name,
                                                        'product_uom_qty': p_line.quantity,
                                                        'price_unit': p_line.medicament_id.product_id.lst_price,
                                                        'account_id': lab_req.patient_id.patient_id.property_account_receivable_id.id,
                                                        'invoice_id': res.id},
                                                       )

            inv_list.append(res.id)
            if inv_list:
                imd = self.env['ir.model.data']
                lab_reqs.write({'is_invoiced': True})
                action = imd.xmlid_to_object('account.action_invoice_tree1')
                list_view_id = imd.xmlid_to_res_id('account.invoice_tree')
                form_view_id = imd.xmlid_to_res_id('account.invoice_form')
                result = {

                    'name': action.name,
                    'help': action.help,
                    'type': action.type,
                    'views': [(list_view_id, 'tree'), (form_view_id, 'form')],
                    'target': action.target,
                    'context': action.context,
                    'res_model': action.res_model,
                }

                if inv_list:
                    result['domain'] = "[('id','in',%s)]" % inv_list
        return result


class create_prescription_shipment(models.Model):
    _name = 'create.prescription.shipment'

    def create_prescription_shipment(self, cr, uid, id, context=None):
        if context == None:
            context = {}
        active_id = context.get('active_id')
        prescription_obj = self.pool.get('medical.prescription.order')
        sale_order_obj = self.pool.get('sale.order')
        sale_order_line_obj = self.pool.get('sale.order.line')

        priscription_record = prescription_obj.browse(cr, uid, active_id, context=context)
        if priscription_record.is_shipped == True:
            raise Warning('All ready Invoiced.')

        res = sale_order_obj.create(cr, uid, {'partner_id': priscription_record.patient_id.id,
                                              'date_invoice': date.today(),
                                              'account_id': priscription_record.patient_id.patient_id.property_account_receivable_id.id,
                                              }, context=context)
        for p_line in priscription_record.prescription_line_ids:
            res1 = sale_order_line_obj.create(cr, uid, {'product_id': p_line.medicament_id.product_id.id,
                                                        'product_uom': p_line.medicament_id.product_id.uom_id.id,
                                                        'name': p_line.medicament_id.product_id.name,
                                                        'product_uom_qty': 1,
                                                        'price_unit': p_line.medicament_id.product_id.lst_price,
                                                        # 'account_id': priscription_record.patient_id.patient_id.property_account_receivable_id.id,
                                                        'order_id': res}, context=context)
        prescription_obj.write(cr, uid, context.get('active_id'), {'is_shipped': True}, context=context)
        sale_order_obj.action_confirm(cr, uid, [res])
        result = sale_order_obj.action_view_delivery(cr, uid, [res])
        return result


class Prescription(models.Model):
    _name = "medical.prescription.order"

    name = fields.Char('Prescription ID')
    patient_id = fields.Many2one('medical.patient', 'Pet')
    prescription_date = fields.Datetime('Prescription Date', default=fields.Date.context_today)
    medical_physician_id = fields.Many2one('medical.physician', 'Prescribing Doctor')
    no_invoice = fields.Boolean('Invoice exempt')
    inv_id = fields.Many2one('account.invoice', 'Invoice')
    doctor_id = fields.Many2one('medical.physician', 'Prescribing Doctor')
    pid1_id = fields.Many2one('medical.appointment', 'Appointment')
    state = fields.Selection([('invoiced', 'To Invoiced'), ('tobe', 'To Be Invoiced')], 'Invoice Status')
    prescription_line_ids = fields.One2many('medical.prescription.line', 'name', 'Prescription Line')
    invoice_done = fields.Boolean('Invoice Done')
    notes = fields.Text('Prescription Note')
    appointment_id = fields.Many2one('medical.appointment', 'Oppointment')
    is_invoiced = fields.Boolean(default=False)
    insurer_id = fields.Many2one('medical.insurance', 'Insurer')
    is_shipped = fields.Boolean(default=False)

    # @api.onchange('patient_id')
    # def on_change_patient_id(self):
    #    self.owner_name_id = self.patient_id.patient_id.owner_id

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('medical.prescription.order') or '/'
        return super(Prescription, self).create(vals)

    @api.multi
    def prescription_report(self):
        return self.env['report'].get_action(self, 'hospital_management.prescription_demo_report')

    @api.onchange('name')
    def onchange_name(self):
        ins_obj = self.env['medical.insurance']
        ins_record = ins_obj.search([('name', '=', self.patient_id.patient_id.id)])
        self.insurer_id = ins_record.id or False

    @api.onchange('p_name')
    def onchange_p_name(self):
        self.pricelist_id = 1 or False


class PrescriptionLine(models.Model):
    _name = "medical.prescription.line"

    name = fields.Many2one('medical.prescription.order', 'Prescription ID')
    medicament_id = fields.Many2one('medical.medicament', 'Medicament')
    indication_id = fields.Char('Indication')
    allow_substitution = fields.Boolean('Allow Substitution')
    form_id = fields.Char('Form')
    prnt = fields.Boolean('Print')
    route_id = fields.Char('Administration Route')
    end_treatement = fields.Datetime('Administration Route')
    dose = fields.Float('Dose')
    dose_unit_id = fields.Many2one('medical.dose.unit', 'Dose Unit')
    qty = fields.Integer('Quantidade')
    common_dosage_id = fields.Many2one('medical.medication.dosage', 'Frequency')
    admin_times = fields.Char('Admin Hours', size=128)
    frequency = fields.Integer('Frequency')
    frequency_unit = fields.Selection(
        [('seconds', 'Seconds'), ('minutes', 'Minutes'), ('hours', 'hours'), ('days', 'Days'), ('weeks', 'Weeks'),
         ('wr', 'When Required')], 'Unit')
    duration = fields.Integer('Treatment Duration')
    duration_period = fields.Selection(
        [('minutes', 'Minutes'), ('hours', 'hours'), ('days', 'Days'), ('months', 'Months'), ('years', 'Years'),
         ('indefine', 'Indefine')], 'Treatment Period')
    quantity = fields.Integer('Quantity')
    review = fields.Datetime('Review')
    refills = fields.Integer('Refills#')
    short_comment = fields.Char('Comment', size=128)
    end_treatment = fields.Datetime('End of treatment')
    start_treatment = fields.Datetime('Start of treatment')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
