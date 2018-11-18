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
from datetime import datetime, timedelta, date
from odoo.exceptions import UserError, Warning, ValidationError
from . medical_map import MedicalMap

class medical_appointments_invoice_wizard(models.TransientModel):
    _name = "medical.appointments.invoice.wizard"

    @api.multi
    def create_invoice(self):
        if self._context == None:
            context = {}
        active_ids = self._context.get('active_ids')
        list_of_ids = []
        lab_req_obj = self.env['medical.appointment']
        sale_order_obj = self.env['sale.order']
        account_invoice_obj = self.env['account.invoice']
        account_invoice_line_obj = self.env['account.invoice.line']
        for active_id in active_ids:
            lab_req = lab_req_obj.browse(active_id)
            if lab_req.is_invoiced == True:
                raise Warning('All ready Invoiced.')
            res = account_invoice_obj.create({'partner_id': lab_req.patient_id.patient_id.id,
                                              'date_invoice': date.today(),
                                              'account_id': lab_req.patient_id.patient_id.property_account_receivable_id.id,
                                              })
            res1 = account_invoice_line_obj.create({
                'product_id': lab_req.consultations.id,
                'product_uom': lab_req.consultations.uom_id.id,
                'name': lab_req.consultations.name,
                'product_uom_qty': 1,
                'price_unit': lab_req.consultations.lst_price,
                'account_id': lab_req.patient_id.patient_id.property_account_receivable_id.id,
                'invoice_id': res.id})
            list_of_ids.append(res.id)
            if list_of_ids:
                imd = self.env['ir.model.data']
                lab_req_obj_brw = lab_req_obj.browse(self._context.get('active_id'))
                lab_req_obj_brw.write({'is_invoiced': True})
                action = imd.xmlid_to_object('account.action_invoice_tree1')
                list_view_id = imd.xmlid_to_res_id('account.invoice_tree')
                form_view_id = imd.xmlid_to_res_id('account.invoice_form')
                result = {
                    'name': action.name,
                    'help': action.help,
                    'type': action.type,
                    'views': [[list_view_id, 'tree'], [form_view_id, 'form']],
                    'target': action.target,
                    'context': action.context,
                    'res_model': action.res_model,

                }
                print("=========================result", result)
                if list_of_ids:
                    result['domain'] = "[('id','in',%s)]" % list_of_ids
                print("=========================result", result)
            return result


class medical_appointment(models.Model):
    _name = "medical.appointment"
    _inherit = 'mail.thread'

    STATUS = [
        ('scheduled', _('Scheduled')),
        ('confirmed', _('Confirmed')),
        ('attendance', _('In Attendance')),
        ('canceled', _('Canceled'))
    ]
    REASONS = [
        ('abandonment', 'Abandonment'),
        ('price', 'Price'),
        ('reschedule', 'Reschedule'),
        ('personal-problem', 'Personal Problem'),
        ('other', 'Other')
    ]

    name = fields.Char(string="Appointment ID", readonly=True, copy=True)
    is_invoiced = fields.Boolean(default=False)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
    inpatient_registration_code = fields.Many2one('medical.inpatient.registration', string="Inpatient Registration")
    patient_status = fields.Selection([
        ('ambulatory', 'Ambulatory'),
        ('outpatient', 'Outpatient'),
        ('inpatient', 'Inpatient'),
    ], 'Patient status', sort=False, default='outpatient')
    owner_id = fields.Many2one(
        'res.partner', string='Owner', required=True, track_visibility='onchange',
        domain="[('is_owner', '=', True)]"
    )
    patient_id = fields.Many2one(
        'medical.patient', string='Patient', required=False, track_visibility='onchange',
        domain="[('owner_id', '=', owner_id)]"
    )
    urgency_level = fields.Selection([
        ('a', 'Normal'),
        ('b', 'Urgent'),
        ('c', 'Medical Emergency'),
    ], 'Urgency Level', sort=False, default="a")
    appointment_date = fields.Datetime(
        string='Appointment Date', required=False, track_visibility='onchange'
    )
    appointment_end = fields.Datetime(
        string='Appointment End', compute='_compute_appointment_end', store=True
    )
    doctor_id = fields.Many2one(
        'medical.physician', string='Physician', required=False, track_visibility='onchange'
    )
    anesthetist_id = fields.Many2one(
        'medical.physician', string="Anesthetist", domain=[('especiality_anesthesiology', '=', True)]
    )
    speciality = fields.Many2one('medical.speciality', 'Speciality')
    comments = fields.Text(string="Info")
    state = fields.Selection([('draft', 'Draft'), ('confirmed', 'Confirm'), ('cancel', 'Cancel'), ('done', 'Done')],
                             string="State", default='draft')
    ped_id1 = fields.Many2many('medical.patient.psc', string='Pediatrics Symptoms Checklist')
    pres_id1 = fields.One2many('medical.prescription.order', 'appointment_id', string='Prescription')
    insurer_id = fields.Many2one('medical.insurance', 'Insurer')
    duration = fields.Float(
        string=_("Scheduled Time")
    )
    building_id = fields.Many2one(
        'medical.hospital.building', string="Building", required=False
    )
    # owner_name = fields.Many2one('res.partner','Owner')
    state = fields.Selection(
        selection=STATUS, string=_("Status"), index=True, default='scheduled', track_visibility='onchange', copy=False
    )
    bed_id = fields.Many2one(
        'medical.hospital.bed', string=_("Baia"), track_visibility='onchange'
    )
    medical_procedure_id = fields.Many2one(
        'product.product',
        string=_("Service"),
        domain=[('medical_type', 'in', map(lambda x: x[0], MedicalMap.TYPE))],
        required=False
    )
    lab_test_type = fields.Selection(
        string="Test Type",
        selection=[('image', _("Imagem")), ('laboratory', _("Laboratory")),]
    )
    service_type = fields.Selection(
        string="Service Type", related="medical_procedure_id.medical_type", selection=MedicalMap.TYPE
    )
    reason_for_cancellation = fields.Selection(
        string="Reason for Cancellation", selection=REASONS, track_visibility='onchange'
    )
    observation_cancellation = fields.Text(
        string="Observation", track_visibility='always'
    )
    requester_id = fields.Many2one(
        'medical.physician', string='Request'
    )
    owner_updated = fields.Boolean(
        string="Owner Updated",
        default=True
    )

    locked = fields.Boolean(
        string="Locked"
    )
    unlocked = fields.Boolean(
        string="Unlocked"
    )
    admission_id = fields.Many2one(
        'medical.inpatient.registration',
        string='Admission'
    )
    map_id = fields.Many2one(
        'medical.map',
        string='Map'
    )
    admission_ids = fields.Many2many(
        'medical.inpatient.registration'
    )
    map_ids = fields.Many2many(
        'medical.map'
    )
    admission_os_openeds = fields.Boolean()

    @api.depends('duration', 'appointment_date')
    def _compute_appointment_end(self):
        if self.duration and self.appointment_date:
            dt = datetime.strptime(self.appointment_date, "%Y-%m-%d %H:%M:%S")
            self.appointment_end = dt + timedelta(hours=self.duration)

    @api.one
    @api.constrains('patient_id', 'doctor_id', 'bed_id', 'appointment_date', 'appointment_end')
    def _check_description(self):
        if self.locked:
            return

        if self.doctor_id:
            args = [
                ('id', '!=', self.id),
                ('doctor_id', '=', self.doctor_id.id),
                ('appointment_date', '>=', self.appointment_date),
                ('appointment_end', '<=', self.appointment_end),
            ]
            search = self.search(args, limit=1)
            if search:
                raise ValidationError(_("The veterinarian is already on schedule."))
            else:
                args = [
                    ('id', '!=', self.id),
                    ('building_id', '=', self.building_id.id),
                    ('appointment_date', '>=', self.appointment_date),
                    ('appointment_end', '<=', self.appointment_end),
                ]
                search = self.search(args, limit=1)
                if search:
                    raise ValidationError(_("this room is already scheduled for this time."))
            args = [
                ('doctor_id', '=', self.doctor_id.id),
                ('date_start', '<=', self.appointment_end),
                ('date_end', '>=', self.appointment_date)
            ]
            appointment_date = fields.Datetime.context_timestamp(
                self, fields.Datetime.from_string(self.appointment_date)
            )
            appointment_end = fields.Datetime.context_timestamp(
                self, fields.Datetime.from_string(self.appointment_end)
            )
            if self.env['medical.physician.schedules.canceled'].search(args, limit=1):
                raise ValidationError(
                    _("The veterinarian does not have available hours on this date. (Canceled).")
                )
            args = [
                ('doctor_id', '=', self.doctor_id.id),
                ('weekday', '=', str(appointment_date.weekday())),
                ('month', '=', appointment_date.month),
                ('year', '=', appointment_date.year),
                ('start_hour', '<=', appointment_date.hour + (appointment_date.minute * 60 / 3600.)),
                ('end_hour', '>=', appointment_end.hour + (appointment_end.minute * 60 / 3600.)),
            ]
            if not self.env['medical.physician.schedules'].search(args, limit=1):
                raise ValidationError(
                    _("The veterinarian does not have available hours on this date. (Schedules).")
                )

    @api.onchange('appointment_date')
    def onchange_service(self):
        self.doctor_id = False

    @api.onchange('medical_procedure_id')
    def onchange_service(self):
        service = self.medical_procedure_id
        if service:
            self.duration = service.time_taken

    @api.onchange('owner_id')
    def onchange_name(self):
        self.patient_id = False

        if self.owner_id:
            last_update = datetime.strptime(
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"%Y-%m-%d %H:%M:%S")\
                          - datetime.strptime(self.owner_id.write_date,"%Y-%m-%d %H:%M:%S")

            if last_update > timedelta(days=90):
                self.owner_id = False
                return {
                    'warning': {
                        'title': _("Attention"),
                        'message': _("This user is outdated, please update the user data before continuing.")
                    }
                }


    @api.model
    def default_get(self, values):
        result = super(medical_appointment, self).default_get(values)
        return result

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('medical.appointment') or 'APT'
        msg_body = 'Appointment created'
        self.message_post(body=msg_body)
        result = super(medical_appointment, self).create(vals)
        return result

    @api.multi
    def write(self, vals):

        if self.check_owner_updated():
            res = super(medical_appointment, self).write(vals)
            return res
        else:
            raise ValidationError(
                _("Please update the Owner before saving this record.")
            )

    @api.onchange('doctor_id')
    def onchange_doctor(self):
        if not self.doctor_id:
            self.speciality = ""
        doc = self.env['medical.speciality'].browse(self.doctor_id.id)
        self.speciality = doc.id

    def check_admission_open(self, owner_id):
        mir = self.env['medical.inpatient.registration']
        domain = [
            ('owner_id', '=', owner_id),
            ('state', 'in', ['start_attendance','open'])
        ]
        return mir.search(domain, limit=1)

    def check_map_open(self, admission_id, map_type):
        omap = self.env['medical.map']
        domain = [
            ('admission_id', '=', admission_id),
            ('name', '=', map_type),
            ('state', '=', 'open')
        ]
        return omap.search(domain, limit=1)

    def check_owner_updated(self):
        if self.owner_id:
            last_update = datetime.strptime(
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")\
                          - datetime.strptime(self.owner_id.write_date, "%Y-%m-%d %H:%M:%S")

            if last_update > timedelta(days=90):
                return False
            else:
                return True
        else:
            return False

    @api.onchange('medical_procedure_id', 'owner_id')
    def onchange_medical_procedure(self):
        msg = ""
        if self.owner_id and self.medical_procedure_id:
            # verificar se tem alguma ficha em aberto
            os_oppened = self.check_admission_open(self.owner_id.id)
            if os_oppened:
                name = self.owner_id.name
                msg += _(u"%s already has an open admission: %s\n" % (name, '/'.join(
                    map(lambda x: x.name, os_oppened)
                )))
                self.admission_ids = os_oppened.ids
                # verificar se tem alguma OS em aberto
                map_open = self.check_map_open(os_oppened.id, self.service_type)
                if map_open:
                    msg += _(u"%s already has an open OS: %s\n" % (name, '/'.join(map(lambda x: x.code, map_open))))
                    self.map_ids = map_open.ids
                else:
                    self.map_ids = []
            else:
                self.admission_ids = []
            if msg:
                self.admission_os_openeds = True
                self.locked = False
                return {
                    'warning': {
                        'title': _("Warning"),
                        'message': msg
                    },
                }
            else:
                self.admission_os_openeds = False

    @api.onchange('owner_id')
    def onchange_owner(self):
        # Verificar se e mau pagador
        if self.owner_id.trust == 'bad' and not self.unlocked:
            self.locked = True
            return {
                'warning': {
                    'title': _("Warning"),
                    'message': _("This client is locked.")
                }
            }

        self.unlocked = False
        self.locked = False


    @api.multi
    def action_update_partner(self):
        self.ensure_one()
        address_form_id = self.env.ref('base.view_partner_form').id
        return {'type': 'ir.actions.act_window',
                'res_model': 'res.partner',
                'view_mode': 'form',
                'views': [(address_form_id, 'form')],
                'res_id': self.owner_id.id,
                'target': 'new',
                'flags': {'form': {'action_buttons': True}}}


    @api.multi
    def action_find_doctor(self, context=None):
        self.ensure_one()
        context = context or {}
        partial = self.env['appointment.start.end.wizard'].create({})

        return {
            'name': "Find Doctor for appointment",
            'view_mode': 'form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'appointment.find.doctor.wizard',
            # 'res_id': partial.id,
            'type': 'ir.actions.act_window',
            'nodestroy': False,
            'target': 'new',
            'flags': {'form': {'action_buttons': False}},
            'domain': '[]',
        }
        #
        # find_doctor_form_id = self.env.ref('hospital_management.action_appointment_evaluation_per_doctor_wizard').id
        # return {'type': 'ir.actions.act_window',
        #         'res_model': 'appointment.start.end.wizard',
        #         'view_mode': 'form',
        #         'views': [(find_doctor_form_id, 'form')],
        #         # 'res_id': self.id,
        #         'target': 'new',
        #         'flags': {'form': {'action_buttons': False}},
        #         'context': {"mychar":'HELLO WORLD'}
        #         }

    @api.multi
    def action_unlock(self):
        self.ensure_one()
        res = {
            'name': _('Unlock Client'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'unlock.client.wizard',
            'target': 'new',
            'context': {},
        }
        return res

    @api.multi
    def confirm_scheduled(self):
        if self.locked:
            raise UserError(_('Please, unlock client to confirm schedule.'))
        self.write({
            'state': 'confirmed',
            'admission_os_openeds': False
        })

    @api.multi
    def confirm_attendance(self):
        mip = self.env['medical.inpatient.registration']
        admission_open = self.check_admission_open(self.owner_id.id)
        if not self.map_id:
            if not admission_open:
                vals = {
                    'owner_id': self.owner_id.id,
                    'patient': self.patient_id.id,
                    'attending_physician': self.doctor_id.id,
                    'hospitalization_date': self.appointment_date
                }
                admission_id = mip.create(vals)
            else:
                admission_id = admission_open
            omap = self.env['medical.map']
            vals = {
                'admission_id': admission_id.id,
                'name': self.medical_procedure_id.medical_type,
                'owner_id': self.owner_id.id,
                'owner_id_invisible': self.owner_id.id,
                'patient_id': self.patient_id.id,
                'patient_id_invisible': self.patient_id.id,
                'doctor_id': self.doctor_id.id,
                'service_id': self.medical_procedure_id.id,
                'start_date': self.appointment_date,
                'state': 'schedule',
                'schedule_state': 'schedule'
            }
            if self.lab_test_type:
                vals['lab_test_type'] = self.lab_test_type
            if self.anesthetist_id:
                vals['sur_anesthetist'] = self.anesthetist_id.id
            map_id = omap.create(vals)
            map_id.onchange_service_id()
            self.write({
                'state': 'attendance',
                'map_id': map_id.id,
                'admission_os_openeds': False
            })
        else:
            self.write({
                'state': 'attendance',
                'admission_os_openeds': False
            })

    @api.multi
    def cancel_scheduled(self):
        self.write({'state': 'canceled'})

    @api.multi
    def set_scheduled(self):
        self.write({'state': 'scheduled'})

    @api.multi
    def print_prescription(self):
        self.filtered(lambda s: s.state == 'draft').write({'state': 'done'})
        if not self.pres_id1:
            raise UserError(_(' No Prescription Added  '))
        return self.env['report'].get_action(self, 'hospital_management.prescription_demo_report')
