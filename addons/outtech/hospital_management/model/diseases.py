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
# import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError

class medical_pathology(models.Model):
    _name = 'medical.pathology'

    name = fields.Char(string="Name",required=True)
    code = fields.Char(string="Code")
    category = fields.Many2one('medical.pathology.category',string="Disease Category")
    line_ids = fields.One2many('medical.pathology.group.member','disease_group',string="Group")
    chromosome = fields.Char(string="Affected Chromosome")
    gene = fields.Char(string="Gene")
    protein = fields.Char(string="Protein")
    info = fields.Text(string="Extra Info")
    diagnostic_suspicion = fields.Many2many('product.template',  'diagnostic_suspicion_product_template_rel',string=_("Product/Service"))
    diagnostic = fields.Many2many('product.template', 'diagnostic_product_template_rel',string=_("Diagnostic"))
    suggested_protocol = fields.Many2many('medical.office.template')
    prescription = fields.Many2many('medical.prescription.order', string=_("Prescription"))

class medical_pathology_group(models.Model):
    _name = 'medical.pathology.group'
    
    name = fields.Char(string="Name",required=True)
    code = fields.Char(string="Code")
    desc = fields.Char(string="Short Description",required=True)
    info = fields.Text(string="Detailed Information")
    
class medical_pathology_category(models.Model):
    _name = 'medical.pathology.category'
    
    name = fields.Char(string="Category Name",required=True)
    active = fields.Boolean(string="Active" , default = True)
    parent_id = fields.Many2one('medical.pathology.category', string="Parent Category")
    
class medical_pathology_group_member(models.Model):
    _name = 'medical.pathology.group.member'
    
    disease_group = fields.Many2one('medical.pathology.group', string="Group", required=True)

class medical_pathology_line(models.Model):
    _name = "medical.pathology.line"



    map_id = fields.Many2one("medical.map", string=_("Map"))
    pathology_id = fields.Many2one("medical.pathology", string=_("Pathology"))
    suspicion = fields.Boolean("Suspicion")
    diagnostic = fields.Boolean("Diagnostic")
    protocol_suggestion = fields.Many2one('medical.office.template', "Protocol Suggestion")
    prescription = fields.Many2one('medical.prescription.order', string=_("Prescription"))

    def unlink(self):
        res = super(medical_pathology_line, self).unlink()

        return res

    @api.multi
    def write(self, vals):
        res = super(medical_pathology_line, self).write(vals)

        return res

    # @api.onchange('suspicion')
    # def onchange_suspicion(self):
    #     if not self._origin:
    #         self._origin = self
    #     update_vals = []
    #
    #     if self.suspicion == True and self.diagnostic == True:
    #         self.diagnostic = False
    #         self.write({'diagnostic': False, })
    #
    #     if self.map_id and self.pathology_id and self.suspicion:
    #         for line in self.pathology_id.diagnostic_suspicion:
    #             v = {
    #                     'map_id': self._origin.map_id.id,
    #                     'pathology_id': self.pathology_id.id,
    #                     'pathology_line_id': self._origin.id,
    #                     'suggested_service': line.id,
    #                 }
    #             self.env['medical.diseases.line'].create(v)
    #             # update_vals.append((0, 0, v))
    #
    #     if not self.suspicion:
    #         disease_ids = self.env['medical.diseases.line'].search([('pathology_line_id', '=', self._origin.id)])
    #         if disease_ids:
    #             for line in disease_ids:
    #                 line.write({'map_id':False})

        # self._origin.map_id.medical_diseases_ids = update_vals

    # @api.onchange('diagnostic')
    # def onchange_diagnostic(self):
    #     if not self._origin:
    #         self._origin = self
    #     update_vals = []
    #
    #     if self.suspicion == True and self.diagnostic == True:
    #         self.suspicion = False
    #         self.write({'suspicion': False})
    #
    #     if self.map_id and self.pathology_id and self.diagnostic:
    #         for line in self.pathology_id.diagnostic:
    #             v = {
    #                     'map_id': self._origin.map_id.id,
    #                     'pathology_id': self.pathology_id.id,
    #                     'pathology_line_id': self._origin.id,
    #                     'suggested_service': line.id,
    #                 }
    #             self.env['medical.diseases.line'].create(v)
    #             # update_vals.append((0, 0, v))
    #
    #     if not self.diagnostic:
    #         disease_ids = self.env['medical.diseases.line'].search([('pathology_line_id', '=', self._origin.id)])
    #         for line in disease_ids:
    #             line.write({'map_id': False})
    #     # self._origin.map_id.medical_diseases_ids = update_vals


class medical_diseases_line(models.Model):
    _name = "medical.diseases.line"

    map_id = fields.Many2one("medical.map", string=_("Map"))
    pathology_id = fields.Many2one("medical.pathology", string=_("Pathology"))
    pathology_line_id = fields.Many2one("medical.pathology.line", string=_("Pathology Line"))
    diagnostic_suspicion = fields.Many2one('medical.inpatient.evaluation', 'Diagnostic Suspicion')
    diagnostic_procedure = fields.Char('Diagnostic Procedure')
    #pathology_line_id = fields.Integer("Pathology Line ID")
    suggested_service = fields.Many2one('product.template', "Suggested Service")
    suggested_bool = fields.Boolean("Suggested", default=True)

    def unlink(self):
        src_diseases_line = self.env['medical.diseases.line'].search([('pathology_line_id', '=', self.id)])
        if src_diseases_line:
            for line in src_diseases_line:
                line.unlink()
        res = super(medical_diseases_line, self).unlink()

        return res