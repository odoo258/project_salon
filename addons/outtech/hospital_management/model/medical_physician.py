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
import pytz
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_TIME_FORMAT
from datetime import timedelta, date, datetime

WEEKDAYS = [
    ('0', _("Monday")),
    ('1', _("Tuesday")),
    ('2', _("Wednesday")),
    ('3', _("Thursday")),
    ('4', _("Friday")),
    ('5', _("Saturday")),
    ('6', _("Sunday"))
]

MONTHS = [
    (1, _("January")),
    (2, _("February")),
    (3, _("March")),
    (4, _("April")),
    (5, _("May")),
    (6, _("June")),
    (7, _("July")),
    (8, _("August")),
    (9, _("September")),
    (10, _("October")),
    (11, _("November")),
    (12, _("December"))
]


class MedicalPhysician(models.Model):
    _name = "medical.physician"

    external = fields.Boolean(
        string="External"
    )
    name = fields.Many2one(
        'res.partner', 'Physician', required=True, domain="[('is_doctor', '=', True)]"
    )
    user_id = fields.Many2one(
        'res.users', 'User', domain="[('partner_id', '=', name)]",
    )
    institution_id = fields.Many2one(
        'res.partner', 'Institution', domain="[('is_institution', '=', True)]"
    )
    crmv = fields.Char(
        string='CRMV', required=True
    )
    state_crm_id = fields.Many2one(
        'res.country.state', string='CRM State', required=True
    )
    info = fields.Text('Extra Info')
    schedule_ids = fields.One2many(
        'medical.physician.schedules', inverse_name='doctor_id', string=_("Schedule Times")
    )
    schedule_canceled_ids = fields.One2many(
        'medical.physician.schedules.canceled', inverse_name='doctor_id', string=_("Schedule Canceled")
    )
    schedule_available_ids = fields.One2many(
        'medical.physician.schedules.available', inverse_name='doctor_id', string=_("Schedule Available")
    )
    building_id = fields.Many2many(
        'medical.hospital.building', string=_("Building"), domain="[('institution', '=', institution_id)]"
    )
    especiality_lab_test = fields.Boolean(
        string="Lab Test"
    )
    especiality_medicament = fields.Boolean(
        string="Medicament"
    )
    especiality_medical_appointment = fields.Boolean(
        string="Medical Appointment"
    )
    especiality_vaccines = fields.Boolean(
        string="Vaccines"
    )
    especiality_intensive_veterinary_medicine = fields.Boolean(
        string="Intensive Veterinary Medicine"
    )
    especiality_surgery = fields.Boolean(
        string="Surgery"
    )
    especiality_anesthesiology = fields.Boolean(
        string="Anesthesiology"
    )
    especiality_specialty = fields.Boolean(
        string="Specialty"
    )
    especiality_esthetics = fields.Boolean(
        string="Esthetics"
    )



    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        sql = """SELECT MPS.doctor_id 
                 FROM   medical_physician_schedules as MPS 
                 WHERE  MPS.weekday   = '{weekday:d}' 
                        AND MPS.month = {month:d} 
                        AND MPS.year  = {year:d} 
                        AND MPS.start_hour  <= {time_start:.12f} 
                        AND {time_end:.12f} <= MPS.end_hour
                 GROUP BY MPS.doctor_id"""

        if 'filter_appointment_end' in self._context.keys() or 'filter_appointment_date' in self._context.keys():
            appointment_date = self._context.get('filter_appointment_date')
            appointment_end = self._context.get('filter_appointment_end')
            date_ini = fields.Datetime.context_timestamp(
                self, fields.Datetime.from_string(appointment_date)
            )
            date_end = fields.Datetime.context_timestamp(
                self, fields.Datetime.from_string(appointment_end)
            )

            float_minute_start = date_ini.hour + date_ini.minute * 60 / 3600.
            float_minute_end = date_end.hour + date_end.minute * 60 / 3600.

            if appointment_date and appointment_end:
                sql = sql.format(
                    weekday=date_ini.weekday(),
                    month=date_ini.month,
                    year=date_ini.year,
                    time_start=float_minute_start,
                    time_end=float_minute_end
                )
                print(sql)
                self._cr.execute(sql)
                doctor_ids = map(lambda x: x['doctor_id'], self._cr.dictfetchall())
                if self._context.get('service_type'):
                    service_type = self._context.get('service_type')
                    if service_type == 'surgery':
                        type = 'especiality_surgery'
                    elif service_type == 'anesthesiology':
                        type = 'especiality_anesthesiology'
                    elif service_type == 'lab_test':
                        type = 'especiality_lab_test'
                    elif service_type == 'hospitalization':
                        type = 'especiality_intensive_veterinary_medicine'
                    elif service_type == 'medical_appointment' or service_type == 'attested':
                        type = 'especiality_medical_appointment'
                    elif service_type == 'medicament':
                        type = 'especiality_medicament'
                    elif service_type == 'vaccines':
                        type = 'especiality_vaccines'
                    elif service_type == 'specialty':
                        type = 'especiality_specialty'
                    elif service_type == 'esthetics':
                        type = 'especiality_esthetics'
                    res = map(lambda x: (x.id, x.name.name), self.env['medical.physician'].search(
                        [('id', 'in', doctor_ids),(type,'=',True)]
                    ))
                else:
                    res = []
                print(res)
                return res
            else:
                return []
        res = super(MedicalPhysician, self).name_search(name=name, args=args, operator=operator, limit=100)
        return res

    @api.onchange('institution_id')
    def onchange_institution(self):
        self.building_id = False

    @api.onchange('name')
    def onchange_name(self):
        user_id = False
        partner_id = self.name
        if partner_id:
            user_id = self.env['res.users'].search([('partner_id', '=', partner_id.id)], limit=1)
        self.user_id = user_id


def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)


class MedicalPhysicianSchedule(models.Model):
    _name = 'medical.physician.schedules'
    _rec_name = 'doctor_id'

    weekday = fields.Selection(
        string="Weekday", required=True, selection=WEEKDAYS
    )
    month = fields.Selection(
        string="Month", required=True, selection=MONTHS
    )
    year = fields.Integer(
        string="Year", required=True
    )
    start_hour = fields.Float(
        string="Start Hour", required=True
    )
    end_hour = fields.Float(
        string="End Hour", required=True
    )
    doctor_id = fields.Many2one(
        'medical.physician', string=_("Doctor")
    )

    def create_availables_schedules(self, vals, create=False):

        if create:
            year = vals.get("year")
            month = vals.get("month")
            start_hour = vals.get("start_hour")
            end_hour = vals.get("end_hour")
            weekday = vals.get("weekday")
        else:
            year = self.year
            month = self.month
            start_hour = self.start_hour
            end_hour = self.end_hour
            weekday = self.weekday

        start_date = date(year,month, 1)
        end_date = date(year, month+1, 1) - timedelta(days=1)

        base = fields.Datetime.context_timestamp(
            self, fields.Datetime.from_string(datetime.today().strftime("%Y-%m-%d"))
        )
        time_fix = -1 * int(base.strftime("%z")[:-2])
        start_hour = '{0:02.0f}:{1:02.0f}:00'.format(*divmod((start_hour+time_fix) * 60, 60))
        end_hour = '{0:02.0f}:{1:02.0f}:00'.format(*divmod((end_hour+time_fix) * 60, 60))

        if weekday:
            for single_date in daterange(start_date, end_date):

                if single_date.weekday() == int(weekday):
                    print(single_date.strftime("%A %d-%m-%Y"))

                    start_datetime = single_date.strftime("%Y-%m-%d") + " " + start_hour
                    end_datetime = single_date.strftime("%Y-%m-%d") + " " + end_hour

                    start_datetime = fields.Datetime.context_timestamp(
                        self, fields.Datetime.from_string(start_datetime)
                    )
                    end_datetime = fields.Datetime.context_timestamp(
                        self, fields.Datetime.from_string(end_datetime)
                    )

                    start_datetime = start_datetime + timedelta(hours=-1*int(start_datetime.strftime("%z")[:-2]))
                    end_datetime = end_datetime + timedelta(hours=-1*int(end_datetime.strftime("%z")[:-2]))

                    args = [
                        ('doctor_id', '=', vals.get('doctor_id', self.doctor_id.id)),
                        ('date_start', '>=', start_datetime.strftime("%Y-%m-%d %H:%M:%S")),
                        ('date_end', '<=', end_datetime.strftime("%Y-%m-%d %H:%M:%S")),
                    ]
                    search = self.env['medical.physician.schedules.available'].search(args, limit=1)
                    if len(search) == 0:
                        available_obj = {
                                'date_start': start_datetime,
                                'date_end': end_datetime,
                                'doctor_id': vals.get('doctor_id', self.doctor_id.id)
                            }
                        self.env['medical.physician.schedules.available'].create(available_obj)
                    else:
                        print("no time available")
    @api.model
    def create(self, vals):
        result = super(MedicalPhysicianSchedule, self).create(vals)
        self.create_availables_schedules(vals, create=True)
        return result

    @api.multi
    def write(self, vals):
        res = super(MedicalPhysicianSchedule, self).write(vals)
        self.create_availables_schedules(vals)
        return res


class MedicalPhysicianScheduleCanceled(models.Model):
    _name = 'medical.physician.schedules.canceled'
    _rec_name = 'doctor_id'

    date_start = fields.Datetime(
        string=_("Date Start"), required=True
    )
    date_end = fields.Datetime(
        string=_("End Date"), required=True
    )
    reason = fields.Char(
        string=_("Reason"), required=True
    )
    doctor_id = fields.Many2one(
        'medical.physician', string=_("Doctor")
    )

    #TODO: Inserir aqui o metodo para modificação de horário livre com:
    def modify_availables_schedules(self, vals):
        args = [
            ('doctor_id', '=', vals.get('doctor_id', self.doctor_id.id)),
            ('date_start', '<=', self.date_start),
            ('date_end', '>=', self.date_end),
        ]
        search = self.env['medical.physician.schedules.available'].search(args, limit=1)

        if search:
            if self.date_start == search.date_start:
                if self.date_end != search.date_end:
                    print("inicio igual")
                    search.date_start = self.date_end
            elif self.date_end == search.date_end:
                if self.date_start != search.date_start:
                    print("final igual")
                    search.date_end = self.date_start
            else:
                print("no meio")
            # available_obj = {
            #     'date_start': self.date_start,
            #     'date_end': self.date_end,
            #     'doctor_id': vals.get('doctor_id', self.doctor_id.id)
            # }
            # self.env['medical.physician.schedules.available'].create(available_obj)


    @api.model
    def create(self, vals):
        result = super(MedicalPhysicianScheduleCanceled, self).create(vals)
        self.modify_availables_schedules(vals)
        return result

    @api.multi
    def write(self, vals):
        res = super(MedicalPhysicianScheduleCanceled, self).write(vals)
        self.modify_availables_schedules(vals)
        return res

    @api.constrains('date_start', 'date_end')
    def _check_time(self):
        if self.date_start > self.date_end:
            raise ValidationError(_("End date can not be greater than start date"))
        else:
            args = [
                ('doctor_id', '=', self.doctor_id.id),
                ('id', '!=', self.id),
                ('date_start', '>=', self.date_start),
                ('date_end', '<=', self.date_end)
            ]
            if self.search(args, limit=1):
                raise ValidationError(_("There is already an odd time"))


class MedicalPhysicianScheduleAvailable(models.Model):
    _name = 'medical.physician.schedules.available'
    _rec_name = 'doctor_id'

    date_start = fields.Datetime(
        string=_("Date Start"), required=True
    )
    date_end = fields.Datetime(
        string=_("End Date"), required=True
    )
    doctor_id = fields.Many2one(
        'medical.physician', string=_("Doctor")
    )