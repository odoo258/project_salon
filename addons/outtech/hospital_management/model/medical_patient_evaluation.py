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

from odoo import models, fields, _


class MedicalSignsAndSympotoms(models.Model):
    _name = 'medical.signs.and.sympotoms'
    _rec_name = 'clincial_id'

    SIGN_OR_SYMPTOM = [
        ('sign', _("Sign")),
        ('symptom', _("Symptom"))
    ]
    # ORM Fields
    inpatient_evaluation_id = fields.Many2one(
        colmodel_name='medical.inpatient.evaluation',
        string=_("Patient Evaluation")
    )
    clincial_id = fields.Many2one(
        colmodel_name='medical.pathology',
        string=_("Sign or Symptom")
    )
    sign_or_symptom = fields.Selection(
        selection=SIGN_OR_SYMPTOM,
        string=_("Subjective/Objective")
    )
    comments = fields.Char(
        string=_("Comments")
    )


class MedicalSecondaryCondition(models.Model):
    _name = 'medical.secondary_condition'
    _rec_name = 'procedure_id'

    # ORM Fields
    inpatient_evaluation_id = fields.Many2one(
        colmodel_name='medical.inpatient.evaluation',
        string=_("Patient Evaluation")
    )
    procedure_id = fields.Many2one(
        colmodel_name='medical.pathology',
        string=_("Pathology")
    )
    comments = fields.Char(
        string=_("Comments")
    )


class MedicalDiagnosticHypotesis(models.Model):
    _name = 'medical.diagnostic_hypotesis'
    _rec_name = 'procedure_id'

    # ORM Fields
    inpatient_evaluation_id = fields.Many2one('medical.inpatient.evaluation', string=_("Patient Evaluation"))
    procedure_id = fields.Many2one('medical.pathology', string=_("Pathology"))
    comments = fields.Char(
        string=_("Comments")
    )


class MedicalDirections(models.Model):
    _name = 'medical.directions'
    _rec_name = 'procedure_id'

    # ORM Fields
    inpatient_evaluation_id = fields.Many2one(
        colmodel_name='medical.inpatient.evaluation',
        string=_("Patient Evaluation")
    )
    procedure_id = fields.Many2one(
        colmodel_name='medical.pathology',
        string=_("Pathology")
    )
    comments = fields.Char(
        string=_("Comments")
    )


