# -*- coding: utf-8 -*-
##############################################################################
#
#
#    Copyright (C) 2015 BrowseInfo(<http://www.browseinfo.in>).
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


class health_center(models.Model):
    _inherit = 'res.partner'

    relationship = fields.Char(string='Relationship')
    relative_id = fields.Many2one('res.partner', string="Relative_id")
    is_patient = fields.Boolean(string='Patient')
    is_owner = fields.Boolean(string='Owner')
    is_person = fields.Boolean(string="Person")
    is_doctor = fields.Boolean(string="Dector")
    is_institution = fields.Boolean(string="Institation")
    is_insurance_company = fields.Boolean(string='Insurance Company')
    is_pharmacy = fields.Boolean(string="Pharmacy")
    insurance = fields.One2many('medical.insurance', 'patient_id')
    domiciliary_id = fields.Many2one('medical.domiciliary.unit')
    patient_ids = fields.One2many(
        'medical.patient', 'owner_id', string='Pets'
    )
    type = fields.Selection(
        [('contact', 'Contact'),
         ('invoice', 'Invoice address'),
         ('delivery', 'Shipping address'),
         ('billing', 'Billing contact')], string='Address Type',
        default='contact',
        help="Used to select automatically the right address according to the context in sales and purchases documents.")

    # vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
