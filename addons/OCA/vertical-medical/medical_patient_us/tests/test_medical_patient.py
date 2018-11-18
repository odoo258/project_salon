# -*- coding: utf-8 -*-
# © 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestMedicalPatient(TransactionCase):

    def setUp(self,):
        super(TestMedicalPatient, self).setUp()
        self.model_obj = self.env['medical.patient']
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
        self.country_id = self.env['res.country'].search([
            ('code', '=', 'US'),
        ],
            limit=1
        )

    def _new_record(self, ref, is_patient=True, country_id=None):
        if not country_id:
            country_id = self.country_id
        return self.model_obj.create({
            'name': 'Test Partner',
            'social_security': ref,
            'is_patient': is_patient,
            'country_id': country_id.id,
        })

    def test_valid_int(self):
        for i in self.valid:
            self.assertTrue(self._new_record(i))

    def test_valid_str(self):
        for i in self.valid:
            self.assertTrue(self._new_record(str(i)))

    def test_invalid_int(self):
        for i in self.invalid:
            with self.assertRaises(ValidationError):
                self._new_record(i)

    def test_invalid_str(self):
        for i in self.invalid:
            with self.assertRaises(ValidationError):
                self._new_record(i)

    def test_valid_but_not_patient(self):
        for i in self.valid:
            self.assertTrue(self._new_record(i, False))

    def test_no_ref(self):
        try:
            self._new_record(ref=None)
            self.assertTrue(True)
        except ValidationError:
            self.fail(
                'Should not raise ValidationError if ref=None'
            )
