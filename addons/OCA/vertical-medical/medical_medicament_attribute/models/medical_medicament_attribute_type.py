# -*- coding: utf-8 -*-
# © 2015 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class MedicalMedicamentAttributeType(models.Model):
    _name = 'medical.medicament.attribute.type'
    name = fields.Char(
        help="Full Name of Attribute Type",
        required=True,
    )
    attribute_ids = fields.One2many(
        string='Attributes',
        comodel_name='medical.medicament.attribute',
        inverse_name='attribute_type_id',
    )
    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)',
         'This attribute type name already exists.'),
    ]
