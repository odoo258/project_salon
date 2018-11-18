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



class medical_medicament(models.Model):
  
    _name = 'medical.medicament'
    _rec_name = 'product_id'
    
    product_id  = fields.Many2one('product.template', 'Name', domain="[('medical_type', '=', 'medicament')]")
    therapeutic_action = fields.Char('Therapeutic effect', help = 'Therapeutic action')
    price = fields.Float('Price')
    category_id = fields.Many2one('medicament.category', 'Category')
    qty_available = fields.Integer('Quantity Available')
    indications = fields.Text('Indications')
    active_component = fields.Char(string="Active Component")
    presentation = fields.Text('Presentation')
    composition = fields.Text('Composition')
    dosage = fields.Text('Dosage Instructions')
    pregnancy = fields.Text('Pregnancy')
    overdosage = fields.Text('Overdosage')
    pregnancy_warning = fields.Boolean('Pregnancy Warning')
    pregnancy_category = fields.Selection([('a','A'),('b','B'), ('c','C'), ('d', 'D'), ('x', 'X'), ('n','N')], help = """"** FDA Pregancy Categories ***CATEGORY A :Adequate and well-controlled human studies have failed to demonstrate a risk to the fetus in the first trimester of pregnancy (and there is no evidence of risk in later trimesters)CATEGORY B : Animal reproduction studies have failed todemonstrate a risk to the fetus and there are no adequate and well-controlled studies in pregnant women OR Animal studies have shown an adverse effect, but adequate and well-controlled studies in pregnant women have failed to demonstrate a risk to the fetus in any trimester.

CATEGORY C : Animal reproduction studies have shown an adverse effect on the fetus and there are no adequate and well-controlled studies in humans, but potential benefits may warrant use of the drug in pregnant women despite potential risks. 

 CATEGORY D : There is positive evidence of human fetal  risk based on adverse reaction data from investigational or marketing experience or studies in humans, but potential benefits may warrant use of the drug in pregnant women despite potential risks.

CATEGORY X : Studies in animals or humans have demonstrated fetal abnormalities and/or there is positive evidence of human fetal risk based on adverse reaction data from investigational or marketing experience, and the risks involved in use of the drug in pregnant women clearly outweigh potential benefits.

CATEGORY N : Not yet classified""")

    adverse_reaction = fields.Text('Adverse Reactions')
    storage = fields.Text('Storage Condition')
    notes = fields.Text('Extra Info')
    
    
    
  


class medical_medication_dosage(models.Model):
    _name = 'medical.medication.dosage'
    
    name = fields.Char(string="Frequency",required=True)
    abbreviation = fields.Char(string="Abbreviation")
    code = fields.Char(string="Code")
    
class medical_dose_unit(models.Model):
    _name = 'medical.dose.unit'
    
    name = fields.Char(string="Unit",required=True)
    desc = fields.Char(string="Description")

class medical_drug_route(models.Model):
    _name = 'medical.drug.route'

    name = fields.Char(string="Route",required=True)
    code = fields.Char(string="Code")

class medical_drug_form(models.Model):
    _name = 'medical.drug.form'

    name = fields.Char(string="Form",required=True)
    code = fields.Char(string="Code")

class medicament_category(models.Model):
    _name = 'medicament.category'

    name = fields.Char(string="Category Name",required=True)
    parent_id = fields.Many2one('medicament.category',string='Parent Category')
