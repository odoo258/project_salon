# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class MedicalLuhnAbstractTestMixer(TransactionCase):

    def setUp(self, model_name='medical.abstract.luhn'):
        super(MedicalLuhnAbstractTestMixer, self).setUp()
        self.model_obj = self.env[model_name]
        self.valid = [
            4532015112830366,
            6011514433546201,
            6771549495586802,
        ]
        self.invalid = [
            4531015112830366,
            6011514438546201,
            1771549495586802,
        ]
        self.country_us = self.env['res.country'].search([
            ('code', '=', 'US'),
        ],
            limit=1,
        )


class TestMedicalLuhnAbstract(MedicalLuhnAbstractTestMixer):

    def test_valid_int(self):
        for i in self.valid:
            self.assertTrue(
                self.model_obj._luhn_is_valid(i),
                'Luhn validity check on int %s did not pass for valid' % i,
            )

    def test_valid_str(self):
        for i in self.valid:
            self.assertTrue(
                self.model_obj._luhn_is_valid(str(i)),
                'Luhn validity check on str %s did not pass for valid' % i,
            )

    def test_invalid_int(self):
        for i in self.invalid:
            self.assertFalse(
                self.model_obj._luhn_is_valid(i),
                'Luhn validity check on int %s did not fail for invalid' % i,
            )

    def test_invalid_str(self):
        for i in self.invalid:
            self.assertFalse(
                self.model_obj._luhn_is_valid(str(i)),
                'Luhn validity check on str %s did not fail for invalid' % i,
            )
