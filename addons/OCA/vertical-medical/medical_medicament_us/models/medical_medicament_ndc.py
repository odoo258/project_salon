# -*- coding: utf-8 -*-
# © 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class MedicalMedicamentNdc(models.Model):
    _name = 'medical.medicament.ndc'
    _description = 'Medical Medicament NDC'

    name = fields.Char(
        string='NDC',
        help='National Drug Code - 10 or 11 digits',
    )
    manufacturer_id = fields.Many2one(
        string='Manufacturer',
        comodel_name='medical.manufacturer',
    )
    medicament_id = fields.Many2one(
        string='Medicament',
        comodel_name='medical.medicament',
        required=True,
    )
