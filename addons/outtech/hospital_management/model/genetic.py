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

from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp

class medical_gentic_risk(models.Model):
    _name = 'medical.genetic.risk'
    _rec_name = 'long_name'
    
    name = fields.Char(string="Name")
    chromosome = fields.Char(string="Affected Chromosome",help="Name of the affected chromosome")
    location = fields.Char(string="Location",help="Locus of the chromosome")
    info = fields.Text(string="Information",help="Name of the protein(s) affected")
    long_name = fields.Char(string="Official Long Name")
    dominance = fields.Selection([('dominant','Dominant'),('recessive','Recessive')],string="Dominance")
    gene_id = fields.Char(string="Gene ID",help="default code from NCBI Entrez database.")
    
