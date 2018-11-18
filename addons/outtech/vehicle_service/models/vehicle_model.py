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
from odoo import models, fields, api

class VehicleModel(models.Model):
    _name = 'vehicle.model'
    _order = 'name'

    name = fields.Char(string='Name', required=True)
    category_id = fields.Many2one('vehicle.category', string='Category', required=True)
    manufacturer_id = fields.Many2one('vehicle.manufacturer', string='Manufacturer', required=True)
    product_id = fields.Many2one('product.product', string='Product', required=True)
    year_ids = fields.Many2many('vehicle.year', string='Years', required=True)
    plan_ids = fields.Many2many('product.product', string='Plans', required=True)

    @api.onchange('category_id')
    def category_id_change(self):
        return {'value': {'manufacturer_id': '', 'model_id': '', 'year_id': ''}}

    @api.onchange('manufacturer_id')
    def manufacturer_id_change(self):
        return {'value': {'model_id': '', 'year_id': ''}}

    @api.onchange('model_id')
    def model_id_change(self):
        return {'value': {'year_id': ''}}
