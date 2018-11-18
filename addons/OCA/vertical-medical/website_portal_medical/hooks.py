# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, SUPERUSER_ID


def _update_patients_legal_rep(cr, registry):
    with cr.savepoint():
        env = api.Environment(cr, SUPERUSER_ID, {})
        patient_model = env['medical.patient']

        patients = patient_model.search([
            ('parent_id', '=', env.ref('base.partner_demo').id)
        ])
        patients.write(
            {'parent_id': env.ref('portal.demo_user0_res_partner').id}
        )
