# -*- coding: utf-8 -*-
# Copyright 2015 ACSONE SA/NV
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestMedicalPatient(TransactionCase):

    def setUp(self):
        super(TestMedicalPatient, self).setUp()
        self.patient_1 = self.env.ref('medical.medical_patient_patient_1')

    def test_toggle_safety_cap_yn(self):
        self.patient_1.write({'safety_cap_yn': False})
        self.patient_1.toggle_safety_cap_yn()
        self.patient_1.refresh()
        self.assertEquals(
            self.patient_1.safety_cap_yn, True
        )

    def test_counseling_yn(self):
        self.patient_1.write({'counseling_yn': False})
        self.patient_1.toggle_counseling_yn()
        self.patient_1.refresh()
        self.assertEquals(
            self.patient_1.counseling_yn, True
        )
