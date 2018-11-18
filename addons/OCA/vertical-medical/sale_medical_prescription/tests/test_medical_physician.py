# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase

import mock


class TestMedicalPhysician(TransactionCase):

    def setUp(self):
        super(TestMedicalPhysician, self).setUp()
        self.physician_5 = self.env.ref(
            'sale_medical_prescription.medical_physician_physician_5'
        )

    def test_compute_verified_by_id(self):
        """ Test verified_by_id properly set to user """
        self.physician_5.is_verified = True
        self.assertTrue(
            self.physician_5.verified_by_id,
        )

    @mock.patch('odoo.addons.sale_medical_prescription.'
                'models.medical_physician.fields.Datetime')
    def test_compute_verified_date(self, mock_datetime):
        """ Test verified_date set with datetime """
        exp = '2016-12-13 05:15:23'
        mock_datetime.now.return_value = exp
        self.physician_5.is_verified = True
        res = self.physician_5.verified_date
        self.assertEquals(
            res, exp,
        )
