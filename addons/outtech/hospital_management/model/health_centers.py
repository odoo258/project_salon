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

from odoo import models, fields, api, _
import openerp.addons.decimal_precision as dp


class MedicalHospital_building(models.Model):
    _name = 'medical.hospital.building'

    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Code")
    extra_info = fields.Text(string="Extra Info")
    institution = fields.Many2one('res.partner', string="Institute")


class medical_hospital_unit(models.Model):
    _name = 'medical.hospital.unit'

    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Code")
    extra_info = fields.Text(string="Extra Info")
    institution = fields.Many2one('res.partner', string="Institution")


class medical_hospital_ward(models.Model):
    _name = 'medical.hospital.ward'

    name = fields.Char(string="Name", required=True)
    institution = fields.Many2one('res.partner', string="Institution")
    building = fields.Many2one('medical.hospital.building', string="Building")
    floor = fields.Integer(string="Floor Number")
    unit = fields.Many2one('medical.hospital.unit', string="Unit")
    gender = fields.Selection([('men', 'Men Ward'), ('women', 'Women Ward'), ('unisex', 'Unisex')], string="Gender",
                              required=True)
    private = fields.Boolean(string="Private")
    bio_hazard = fields.Boolean(string="Bio Hazard")
    number_of_beds = fields.Integer(string="Number Of Beds")
    telephone = fields.Boolean(string="Telephone Access")
    private_bathroom = fields.Boolean(string="Private Bathroom")
    tv = fields.Boolean(string="Television")
    ac = fields.Boolean(string="Air Conditioning")
    guest_sofa = fields.Boolean(string="Guest Sofa Bed")
    internet = fields.Boolean(string="Internet Access")
    microwave = fields.Boolean(string="Microwave")
    refrigerator = fields.Boolean(string="Refrigetator")
    state = fields.Selection([('beds_available', 'Beds Available'), ('full', 'Full'), ('na', 'Not Available')],
                             string="Status")
    extra_info = fields.Text(string="Extra Info")


class medical_hospital_bed(models.Model):
    _name = 'medical.hospital.bed'

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('hospital_bed_seq')
        result = super(medical_hospital_bed, self).create(vals)
        return result

    name = fields.Char(string="Bed Code", copy=False, readonly=True, index=True)
    bed_type = fields.Selection(
        [('gatch', 'Gatch Bed'), ('electric', 'Electric'), ('stretcher', 'Stretcher'), ('low_bed', 'Low Bed'),
         ('low_air', 'Low Air Loss'), ('c_electric', 'Circo Electric'), ('clinitron', 'Clinitron')], required=True,
        string="Admission Type")
    state = fields.Selection(
        [('occuiped', 'Occuiped'), ('free', 'Free'), ('reserved', 'Reserved'), ('na', 'Not Available')],
        string="Status")
    extra_info = fields.Text(string="Extra Info")
    ward = fields.Many2one('medical.hospital.ward', string="Ward")
    telephone_number = fields.Char(string="Telephone Number")


class medical_hospital_oprating_room(models.Model):
    _name = 'medical.hospital.oprating.room'

    name = fields.Char(string="Name", required=True, size=128)
    building = fields.Many2one('medical.hospital.building', string="Building")
    extra_info = fields.Text(string="Extra Info")
    institution = fields.Many2one('res.partner', string="Institution")
    unit = fields.Many2one('medical.hospital.unit', string="Unit")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:s
