# coding=utf-8
# Author: Christian Douglas <christian.douglas.alcantara@gmail.com>
from odoo import models, fields, api, _
from odoo.exceptions import Warning, ValidationError
from datetime import datetime, timedelta

class CreateAppointmentWizard(models.TransientModel):
    _name = 'create.appointment.wizard'
    owner_id = fields.Many2one(
        'res.partner', string='Owner'
    )
    patient_id = fields.Many2one(
        'medical.patient', string='Patient'
    )
    doctor_id = fields.Many2one(
        'medical.physician', string='Physician'
    )
    medical_procedure_id = fields.Many2one(
        'product.template', string=_("Service"),
        domain="[('medical_type', '=', type)]",
    )
    appointment_date = fields.Datetime(
        string='Appointment Date', required=False
    )
    appointment_end = fields.Datetime(
        string='Appointment End', compute='_compute_appointment_end', store=True
    )
    building_id = fields.Many2one(
        'medical.hospital.building', string="Building", required=False
    )
    type = fields.Char()

    @api.model
    def default_get(self, fields):
        context = self._context
        res = super(CreateAppointmentWizard, self).default_get(fields)
        omap = self.env['medical.map'].browse(context.get('active_id'))
        res['owner_id'] = omap.owner_id.id
        res['patient_id'] = omap.patient_id.id
        res['doctor_id'] = omap.doctor_id.id
        res['type'] = omap.name
        return res

    @api.depends('medical_procedure_id', 'appointment_date')
    def _compute_appointment_end(self):
        if self.medical_procedure_id and self.appointment_date:
            dt = datetime.strptime(self.appointment_date, "%Y-%m-%d %H:%M:%S")
            self.appointment_end = dt + timedelta(hours=self.medical_procedure_id.time_taken)


    @api.one
    def action_create_appointment(self):
        self.ensure_one()
        context = self._context
        # CHECK
        args = [
            ('doctor_id', '=', self.doctor_id.id),
            ('appointment_date', '>=', self.appointment_date),
            ('appointment_end', '<=', self.appointment_end),
        ]
        omap = self.env['medical.appointment']
        search = omap.search(args, limit=1)
        if search:
            raise ValidationError(_("The veterinarian is already on schedule."))
        else:
            args = [
                ('building_id', '=', self.building_id.id),
                ('appointment_date', '>=', self.appointment_date),
                ('appointment_end', '<=', self.appointment_end),
            ]
            search = omap.search(args, limit=1)
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
        if not self.env['medical.physician.schedules'].search_count(args):
            raise ValidationError(
                _("The veterinarian does not have available hours on this date. (Schedules).")
            )
        # CREATE APPOINTMENT
        medical_appointment = self.env['medical.appointment']
        o_map = self.env['medical.map']
        active_id = context.get('active_id')

        vals = dict(
            owner_id=self.owner_id.id,
            patient_id=self.patient_id.id,
            doctor_id=self.doctor_id.id,
            medical_procedure_id=self.medical_procedure_id.id,
            appointment_date=fields.Datetime.from_string(self.appointment_date),
            appointment_end=fields.Datetime.from_string(self.appointment_end),
            building_id=self.building_id.id,
            service_type=self.type,
            map_id=active_id,
            duration=self.medical_procedure_id.time_taken
        )
        medical_appointment.create(vals)
        medical_map = o_map.browse(active_id)
        medical_map.state = 'schedule'
