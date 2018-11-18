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
from openerp import api, fields, models, _


class medical_patient_disease(models.Model):
    _name = "medical.patient.disease"
    _rec_name = 'patient_id'

    pathology_id = fields.Many2one('medical.pathology','Disease', required=True)
    disease_severity =  fields.Selection([('1_mi','Mild'),
                               ('2_mo','Moderate'),
                               ('3_sv','Severe')],'Severity')
    status =  fields.Selection([('c','Chronic'),
                               ('s','Status quo'),
                               ('h','Healed'),
                               ('i','Improving'),
                               ('w','Worsening')],'Status of the disease')
    is_infectious = fields.Boolean('Infectious Disease')
    is_active = fields.Boolean('Active disease')
    short_comment = fields.Char('Remarks')
    diagnosis_date = fields.Date('Date of Diagnosis')
    healed_date = fields.Date('Healed')
    age = fields.Integer('Age when diagnosed')
    doctor_id = fields.Many2one('medical.physician','Physician')
    is_allergic = fields.Boolean('Allergic Disease')
    allergy_type =  fields.Selection([('da','Drag Allergy'),
                               ('fa','Food Allergy'),
                               ('ma','Misc Allergy'),
                               ('mc','Misc Contraindication')],'Allergy type')
    pregnancy_warning = fields.Boolean('Pregnancy warning')
    week_of_pregnancy = fields.Integer('Contracted in pregnancy week #')
    is_on_treatment = fields.Boolean('Currently on Treatment')
    treatment_description = fields.Char('Treatment Description')
    date_start_treatment = fields.Date('Start of treatment')
    date_stop_treatment = fields.Date('End of treatment')
    psc_cod_id = fields.Many2one('medical.procedure','Code')
    patient_id = fields.Many2one('medical.patient',string="Patient")
    new_born_id = fields.Many2one('medical.newborn',string="Newborn")
    extra_info = fields.Text('info')



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: