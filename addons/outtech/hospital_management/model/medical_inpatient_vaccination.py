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
from odoo import fields, models, _


class MedicalVaccination(models.Model):
    _name = 'medical.vaccination'
    # ORM FIELDS
    medical_inpatient_registration_id = fields.Many2one(
        'medical.inpatient.registration',
        string=_("Inpatiente Registration"), required=True
    )
    vaccine = fields.Many2one(
        'product.product',
        string=_("Name"), required=True
    )
    institution = fields.Many2one(
        'res.partner',
        string=_("Institution")
    )
    next_dose_date = fields.Datetime(
        string=_("Next Dose")
    )
    vaccine_expiration_date = fields.Datetime(
        string=_("Expiration Date"),
        required=True
    )
    observations = fields.Char(
        string=_("Observations")
    )
    dose = fields.Integer(
        string=_("Dose Number"), required=True
    )
    date = fields.Datetime(
        string=_("Date"), required=True
    )
    vaccine_lot = fields.Char(
        string=_("Lot Number")
    )
    new_born_id = fields.Many2one(
        'medical.newborn',
        string=_("Newborn")
    )