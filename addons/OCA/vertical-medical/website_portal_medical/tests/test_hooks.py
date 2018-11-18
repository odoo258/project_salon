# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestHooks(TransactionCase):

    def setUp(self):
        super(TestHooks, self).setUp()
        self.patient_mod = self.env['medical.patient']

    def test__update_patients_legal_rep(self):
        """ Test all demo patients legal rep set to portal partner """
        patient = self.patient_mod.search([], limit=1)
        self.assertEquals(
            patient.parent_id,
            self.env.ref('portal.demo_user0_res_partner')
        )
