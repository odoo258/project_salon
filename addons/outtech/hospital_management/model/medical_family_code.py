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
from openerp import api, fields, models, _

class medical_family_disease(models.Model):
    
    _name = 'medical.family.disease'
    
    medial_pathology_id = fields.Many2one('medical.pethology', 'Disease',required=True)
    relative = fields.Selection([('m','Mother'), ('f','Father'), ('b', 'Brother'), ('s', 'Sister'), ('a', 'aunt'), ('u', 'Uncle'), ('ne', 'Nephew'), ('ni', 'Niece'), ('gf', 'GrandFather'), ('gm', 'GrandMother')])
    metrnal = fields.Selection([('m', 'Maternal'),('p', 'Paternal')])
    
class medical_family_code(models.Model):

    _name = "medical.family_code"

    name = fields.Char(string="Name", required=True)
    operational_sector_id = fields.Many2one('medical.operational_sector', string="Operational Sector")
    members_ids = fields.Many2many('res.partner',string="Members")
    info = fields.Text(string="Extra info")
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: