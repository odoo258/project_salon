# -*- coding: utf-8 -*-
# Copyright 2004 Tech-Receptives
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class MedicalPatient(models.Model):
    _inherit = 'medical.patient'

    medication_ids = fields.One2many(
        string='Medications',
        comodel_name='medical.patient.medication',
        inverse_name='patient_id',
        help='Medications that the patient is currently on',
    )

    count_medication_ids = fields.Integer(
        compute='_compute_count_medication_ids',
        string='Medications',
    )

    @api.multi
    def _compute_count_medication_ids(self):
        for rec_id in self:
            rec_id.count_medication_ids = len(rec_id.medication_ids)
