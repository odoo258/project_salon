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

class medical_patient_medication(models.Model):
    _name = 'medical.patient.medication'
    
    medicament = fields.Many2one('medical.medicament',string='Medicament',required=True)
    medical_patient_medication_id1 = fields.Many2one('medical.patient',string='Medication')
    is_active = fields.Boolean(string='Active', default = True)
    start_treatment = fields.Datetime(string='Start Of Treatment',required=True)
    course_completed = fields.Boolean(string="Course Completed")
    doctor = fields.Many2one('medical.physician',string='Physician')
    indication = fields.Many2one('medical.pathology',string='Indication')
    end_treatment = fields.Datetime(string='End Of Treatment',required=True)
    discontinued = fields.Boolean(string='Discontinued')
    form = fields.Many2one('medical.drug.form',string='Form')
    route = fields.Many2one('medical.drug.route',string=" Administration Route ")
    dose = fields.Float(string='Dose')
    qty = fields.Integer(string='X')
    dose_unit = fields.Many2one('medical.dose.unit',string='Dose Unit')
    duration = fields.Integer(string="Treatment Duration")
    duration_period = fields.Selection([('minutes','Minutes'),
                                        ('hours','hours'),
                                        ('days','Days'),
                                        ('months','Months'),
                                        ('years','Years'),
                                        ('indefine','Indefine')],string='Treatment Period')
    common_dosage = fields.Many2one('medical.medication.dosage',string='Frequency')
    admin_times = fields.Char(string='Admin Hours')
    frequency = fields.Integer(string='Frequency')
    frequency_unit = fields.Selection([('seconds','Seconds'),
                                       ('minutes','Minutes'),
                                       ('hours','hours'),
                                       ('days','Days'),
                                       ('weeks','Weeks'),
                                       ('wr','When Required')],string='Unit')
    notes =fields.Text(string='Notes')
    medical_patient_medication_id = fields.Many2one('medical.patient','Patient')
    
