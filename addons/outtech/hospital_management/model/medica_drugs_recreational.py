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

class medical_drugs_recreational(models.Model):
    _name="medical.drugs_recreational"

    name = fields.Char('Name')
    street_name = fields.Char('Street names')
    toxicity = fields.Selection([
            ('0', 'None'),
            ('1', 'Low'),
            ('2', 'High'),
            ('3', 'Extreme'),
        ], 'Toxicity', sort=False)
    addiction_level = fields.Selection([
            ('0', 'None'),
            ('1', 'Low'),
            ('2', 'High'),
            ('3', 'Extreme'),
        ], 'Dependence', sort=False)
    legal_status = fields.Selection([
            ('0', 'Legal'),
            ('1', 'llgeal'),
        ], 'Legal Status', sort=False)
    category = fields.Selection([
            ('cannabinoids', 'Cannabinoids'),
            ('depressant', 'Depressant'),
            ('dissociative', 'Dissociative Anesthetics'),
            ('hallucinogens', 'Hallucinogens'),
            ('opioide', 'Opioide'),
            ('stimulants', 'Stimulants'),
            ('other', 'Other'),
        ], 'Category', sort=False)
    dea_schedule_i = fields.Boolean('DEA schedule I')
    dea_schedule_ii = fields.Boolean('II')
    dea_schedule_iii = fields.Boolean('III')
    dea_schedule_iv = fields.Boolean('IV')
    dea_schedule_v = fields.Boolean('V')
    withdrawal_level = fields.Integer('Withdrawal')
    reinforcement_level = fields.Integer('Reinforcement')
    tolerance_level = fields.Integer('Tolerance')
    dependence_level = fields.Integer('Dependence')
    intoxication_level = fields.Integer('Intoxication')
    route_oral = fields.Boolean('Oral')
    route_inhaling = fields.Boolean('Smoke / Inhale')
    route_popping = fields.Boolean('Skin Popping')
    route_sniffing = fields.Boolean('Sniffing')
    route_injection = fields.Boolean('Injection')
    info = fields.Text('info')
