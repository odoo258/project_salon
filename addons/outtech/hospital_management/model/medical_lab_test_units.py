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
from openerp import api, fields, models, _
# classes under cofigration menu of laboratry 

class medical_lab_test_units(models.Model):

    _name = 'medical.lab.test.units'
    
    name = fields.Char('Name', required = True)
    code = fields.Char('Code')

class medical_test_critearea(models.Model):
    
    _name = 'medical_test.critearea'
    
    test_id = fields.Many2one('medical.test_type',)
    test_name = fields.Char('Test Name',)
    seq = fields.Integer('Sequence', default=1)
    medical_test_type_id = fields.Many2one ('medical.test_type', 'Test Type')
    medical_lab_id = fields.Many2one('medical.lab', 'Medical Lab Result')
    warning = fields.Boolean('Warning')
    excluded = fields.Boolean('Excluded')
    lower_limit = fields.Float('Lower Limit')
    upper_limit = fields.Float('Upper Limit')
    units_id = fields.Many2one('medical.lab.test.units', 'Units')
    result = fields.Float('Result')
    result_text = fields.Char('Result Text')
    normal_range = fields.Char('Normal Range')
    remark = fields.Text('Remarks')

class medical_test_type(models.Model):

    _name = 'medical.test_type'

    name = fields.Char('Name', required = True)
    code = fields.Char('Code' , required = True)
    critearea_ids = fields.One2many('medical_test.critearea', 'test_id','Critearea')
    service = fields.Many2one('product.product','Service' , required = True)
    info = fields.Text('Extra Information')
      

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: