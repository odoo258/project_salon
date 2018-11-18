# -*- coding: utf-8 -*-
# © 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class MedicalPharmacy(models.Model):
    _inherit = 'medical.pharmacy'

    napb_num = fields.Char(
        string='NAPB #',
        comodel_name='res.partner.id_number',
        compute=lambda s: s._compute_identification(
            'napb_num', 'NAPB',
        ),
        inverse=lambda s: s._inverse_identification(
            'napb_num', 'NAPB',
        ),
        help='National Boards of Pharmacy Id # - 7 digits',
    )
    medicaid_num = fields.Char(
        string='Medicaid #',
        comodel_name='res.partner.id_number',
        compute=lambda s: s._compute_identification(
            'medicaid_num', 'MEDICAID',
        ),
        inverse=lambda s: s._inverse_identification(
            'medicaid_num', 'MEDICAID',
        ),
        help='Medicaid ID # - 9 digits, 1 alpha character',
    )
    npi_num = fields.Char(
        string='NPI #',
        comodel_name='res.partner.id_number',
        compute=lambda s: s._compute_identification(
            'npi_num', 'NPI',
        ),
        inverse=lambda s: s._inverse_identification(
            'npi_num', 'NPI',
        ),
        help="National Provider Identifier - 10 digits",
    )
