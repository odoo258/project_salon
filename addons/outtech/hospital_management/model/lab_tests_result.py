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
from odoo import api, fields, models, _
from datetime import date, datetime


# classes under  menu of laboratry

class medical_lab(models.Model):
    _name = 'medical.lab'
    # _rec_name = 'test_id'

    name = fields.Char('ID')
    test_id = fields.Many2one('medical.test_type', 'Test Type', required=True)
    date_analysis = fields.Datetime('Date of the Analysis', default=datetime.now())
    patient_id = fields.Many2one('medical.patient', 'Patient', required=True)
    date_requested = fields.Datetime('Date requested', default=datetime.now())

    pathologist_id = fields.Many2one('medical.physician', 'Pathologist')
    requestor_id = fields.Many2one('medical.physician', 'Physician', required=True)
    critearea = fields.One2many('medical_test.critearea', 'medical_lab_id', 'Critearea')
    results = fields.Text('Results')
    diagnosis = fields.Text('Diagnosis')

    @api.model
    def create(self, val):
        val['name'] = self.env['ir.sequence'].next_by_code('ltest_seq')
        result = super(medical_lab, self).create(val)
        if val.get('test_id'):
            critearea_obj = self.env['medical_test.critearea']
            criterea_ids = critearea_obj.search([('test_id', '=', val['test_id'])])
            for id in criterea_ids:
                critearea_obj.write({'medical_lab_id': result})

        return result
