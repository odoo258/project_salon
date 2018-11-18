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
from datetime import datetime


class MedicalSurgery(models.Model):
    _name = "medical.surgery"

    name = fields.Many2one('medical.procedure', string='Code')
    medical_inpatient_registration_id = fields.Many2one(
        'medical.inpatient.registration',
        string=_("Inpatiente Registration"), required=True
    )
    description = fields.Char('Description')
    pathology_id = fields.Many2one('medical.pathology', 'Base condition')
    classification = fields.Selection([
        ('o', 'Optional'),
        ('r', 'Required'),
        ('u', 'Urgent'),
        ('e', 'Emergency'),
    ], 'Surgery Classification', sort=False)
    date = fields.Datetime('Date of the surgery')
    age = fields.Char('Patient Age')
    surgeon_id = fields.Many2one('medical.physician', 'Surgeon')
    anesthetist_id = fields.Many2one('medical.physician', 'Anesthetist')
    operating_room_id = fields.Many2one('medical.hospital.oprating.room', 'Operating Room')
    surgery_end_date = fields.Datetime('End of the surgery')
    surgery_length = fields.Char('Duration')
    signed_by_id = fields.Many2one('medical.physician', 'Signed by')
    preop_bleeding_risk = fields.Boolean('Risk of Massive bleeding')
    preop_oximeter = fields.Boolean('Pulse Oximeter in place')
    preop_site_marking = fields.Boolean('Surgical Site Marking')
    preop_antibiotics = fields.Boolean('Antibiotic Prophylaxis')
    preop_sterility = fields.Boolean('Sterility confirmed')
    preop_mallampati = fields.Selection([
        ('class 1', 'Class 1: Full visibility of tonsils, uvula and soft palate'),
        ('class 2', 'Class 2: Visibility of hard and soft palate, upper portion of tonsils and uvula'),
        ('class 3', 'Class 3: Soft and hard palate and base of the uvula are visible'),
        ('class 4', 'Class 4: Only hard palate visible'),
    ], 'Mallampati Score', sort=False)
    preop_rcri = fields.Many2one('medical.rcri', 'RCRI')
    preop_asa = fields.Selection([
        ('ps1', 'PS 1: Normal healthy patient'),
        ('ps2', 'PS 2: Patients with mild systemic disease'),
        ('ps3', 'PS 3: Patients with severe systemic disease'),
        ('ps4', 'PS 4: Patients with severe systemic disease that is a constant threat to life'),
        ('ps5', 'PS 5: Moribund patients who are not expected to survive without the operation'),
        ('ps6', 'PS 6: A declared brain-dead patient who organs are being removed for donor purposes'),
    ], 'ASA PS', sort=False)
    procedures_ids = fields.One2many('medical.operation', 'medi_surg_id')
    extra_info = fields.Text(string="Extra Info")
    anesthesia_report = fields.Text(string="Anesthesia Report")

    @api.onchange('date', 'surgery_end_date')
    def onchange_duration(self):
        if self.date and self.surgery_end_date:
            dt1 = self.date
            dt2 = self.surgery_end_date
            d1 = datetime.strptime(dt1, "%Y-%m-%d %H:%M:%S")
            d2 = datetime.strptime(dt2, "%Y-%m-%d %H:%M:%S")
            rd = d2 - d1
            houser = rd // 3600
            val = str((rd.seconds // 3600) % 3600)
            self.surgery_length = str(rd.seconds // 3600) + '' + 'h' + ' ' + str((rd.seconds // 60) % 60) + '' + 'm'

    @api.multi
    def done(self):
        self.write({
            'state': 'done'
        })


class medical_operation(models.Model):
    _name = 'medical.operation'

    procedures = fields.Many2one('medical.procedure', string='Code')
    notes = fields.Text(string='Notes')
    medi_surg_id = fields.Many2one('medical.surgery', 'Surgery')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
