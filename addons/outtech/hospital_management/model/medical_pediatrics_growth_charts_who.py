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

class medical_pediatrics_growth_charts_who(models.Model):
    _name = 'medical.pediatrics.growth.charts.who'
    
    name = fields.Selection([
                             ('l/h-f-a','Length/height For age'),
                             ('w-f-a','Weight for age'),
                             ('bmi-f-a','Body mass index for age (BMI for age)')],
                            string='Indicator')
    sex = fields.Selection([('m','Male'),('f','Female')],string='sex')
    measure = fields.Selection([('p','percentile'),('z','Z-scores')],string='Measure')
    type = fields.Char(string="Type")
    month = fields.Integer(string="Month")
    value = fields.Float(string='Value')