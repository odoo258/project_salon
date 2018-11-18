# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2017 - OutTech (<http://www.outtech.com.br>).
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

from odoo import api, fields, models, tools, _
import re


class VehiclePartner(models.Model):
    _name = 'vehicle.partner'
    _order = 'partner_id'
    _description = 'Vehicle Partner'

    partner_id = fields.Many2one('res.partner', string='Partner', required=True)
    owner_name = fields.Char(string='Owner Name', required=True)
    renavam = fields.Char(string='Renavam', required=True)
    plate = fields.Char(string='Plate', size=8, required=True)
    category_id = fields.Many2one('vehicle.category', string='Category', required=True)
    manufacturer_id = fields.Many2one('vehicle.manufacturer', string='Manufacturer', required=True)
    model_id = fields.Many2one('vehicle.model', string='Model', required=True)
    year_id = fields.Many2one('vehicle.year', string='Year', required=True)

    _sql_constraints = [
        ('plate_uniq', 'unique(plate)', _('Plate already registered!'))
    ]

    @api.multi
    def name_get(self):
        res = []
        for vehicle in self:
            res.append((vehicle.id, _('[%s] %s') % (vehicle.model_id.name, vehicle.plate)))
        return res

    @api.onchange('plate')
    def plate_vehicle_change(self):

        if self.plate:

            plate_upper = self.plate.upper()

            val = re.sub('[^A-Z0-9]', '', plate_upper)

            if not len(val) == 7:
                return {'warning': {'title': _('WARNING'), 'message': _('Invalid Plate')}}

            for char in val[0:3]:
                if not char.isalpha():
                    return {'warning': {'title': _('WARNING'), 'message': _('Invalid Plate')}}

            for number in val[3:]:
                try:
                    int(number)
                except:
                    return {'warning': {'title': _('WARNING'), 'message': _('Invalid Plate')}}

            format_plate = val[0:3] + '-' + val[3:]

            return {'value': {'plate': format_plate}}

        return {'value': {}}

    @api.onchange('category_id')
    def category_id_change(self):
        return {'value': {'manufacturer_id': '', 'model_id': '', 'year_id': ''}}

    @api.onchange('manufacturer_id')
    def manufacturer_id_change(self):
        return {'value': {'model_id': '', 'year_id': ''}}

    @api.onchange('model_id')
    def model_id_change(self):
        return {'value': {'year_id': ''}}


class VehiclePartnerWebSite(models.Model):
    _name = 'vehicle.partner.website'
    _order = 'partner_id'
    _description = 'Vehicle Partner to WebSite'

    partner_id = fields.Many2one('res.partner', string='Partner', required=True)
    owner_name = fields.Char(string='Owner Name')
    renavam = fields.Char(string='Renavam')
    plate = fields.Char(string='Plate', size=8)
    category_id = fields.Many2one('vehicle.category', string='Category')
    manufacturer_id = fields.Many2one('vehicle.manufacturer', string='Manufacturer')
    model_id = fields.Many2one('vehicle.model', string='Model')
    year_id = fields.Many2one('vehicle.year', string='Year')
    plan_id = fields.Many2one('product.product', string='Plan')
    state = fields.Selection([('draft','Draft'),('confirmed','Confirmed')], 'State')
