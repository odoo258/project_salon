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

from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp

class medical_operational_area(models.Model):
    _name = 'medical.operational_area'
    
    name = fields.Char(string="Name",required=True)
    info = fields.Text(string="Extra Info")
    operational_sector_ids = fields.One2many('medical.operational_sector','operational_area_id',string="Operational sector")
    
class medical_operational_sector(models.Model):
    _name = 'medical.operational_sector'
    
    name = fields.Char(string="Name",required=True,size=128)
    info = fields.Text(string="Extra Info")
    operational_area_id = fields.Many2one('medical.operational_area',string="Operational Area")
