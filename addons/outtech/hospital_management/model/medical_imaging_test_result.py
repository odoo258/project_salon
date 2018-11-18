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

from openerp import models, fields, api, _

class medical_imaging_test_result(models.Model):
    _name = 'medical.imaging.test.result'
    
    name = fields.Char(string="Name",default='IMGR')
    test_date = fields.Datetime(string="Date", default = fields.Date.context_today)
    request_id = fields.Many2one('medical.imaging.test.request',string="Test request", readonly=True)
    request_date = fields.Datetime(string="Request Date", readonly=True)
    test_id = fields.Many2one('medical.imaging.test','Test', readonly=True)
    patient_id = fields.Many2one('medical.patient','Patient', readonly=True)
    physician_id = fields.Many2one('medical.physician','Physician', required = True)
    images_ids = fields.One2many('ir.attachment','imaging_result_id','Images')
    comments = fields.Text(string="Comments")


    @api.model
    def create(self, vals):
        if vals.get('name', 'IMGR') == 'IMGR':
            vals['name'] = self.env['ir.sequence'].next_by_code('medical.imaging.test.result') or 'IMGR'
        result = super(medical_imaging_test_result, self).create(vals)
        return result


class ir_attachment(models.Model):
    _inherit = 'ir.attachment'

    imaging_result_id = fields.Many2one('medical.imaging.test.result')


