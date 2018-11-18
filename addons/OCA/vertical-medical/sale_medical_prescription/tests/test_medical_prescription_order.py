# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase

import mock


class TestMedicalPrescriptionOrder(TransactionCase):

    def setUp(self):
        super(TestMedicalPrescriptionOrder, self).setUp()
        self.rx_7 = self.env.ref(
            'sale_medical_prescription.'
            'medical_prescription_prescription_order_7'
        )

    def test_compute_verified_is_verified(self):
        """ Test verify_user_id populated if verified """
        self.rx_7.verify_method = 'doctor_phone'
        self.assertTrue(
            self.rx_7.is_verified,
        )

    def test_compute_verified_verify_user_id(self):
        """ Test verify_user_id populated if verified """
        self.rx_7.verify_method = 'doctor_phone'
        self.assertTrue(
            self.rx_7.verify_user_id,
        )

    @mock.patch('odoo.addons.sale_medical_prescription.'
                'models.medical_prescription_order.fields.Datetime')
    def test_compute_verified_date(self, mock_datetime):
        """ Test verify_user_id properly set to user """
        exp = '2016-12-13 05:15:23'
        mock_datetime.now.return_value = exp
        self.rx_7.verify_method = 'doctor_phone'
        res = self.rx_7.verify_date
        self.assertEquals(
            res, exp,
        )
