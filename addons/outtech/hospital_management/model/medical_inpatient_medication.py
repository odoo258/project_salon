# -*- coding: utf-8 -*-
from odoo import models, fields, _


class MedicalInpatientMedication(models.Model):
    _name = 'medical.inpatient.medication1'

    DURATION_PERIOD = [
        ('minutes', _("Minutes")),
        ('hours', _("hours")),
        ('days', _("Days")),
        ('months', _("Months")),
        ('years', _("Years")),
        ('indefine', _("Indefine"))
    ]
    FREQUENCY_UNIT = [
        ('seconds', _("Seconds")),
        ('minutes', _("Minutes")),
        ('hours', _("hours")),
        ('days', _("Days")),
        ('weeks', _("Weeks")),
        ('wr', _("When Required"))
    ]
    # ORM FIELDS
    medical_inpatient_registration_id = fields.Many2one(
        'medical.inpatient.registration',
        string=_("Inpatiente Registration"), required=True
    )
    medicament = fields.Many2one(
        'medical.medicament',
        string=_("Medicament"), required=True)
    medical_patient_medication_id = fields.Many2one(
        'medical.patient',
        string=_("Medication")
    )
    is_active = fields.Boolean(
        string=_("Active"), default=True
    )

    start_treatment = fields.Datetime(
        string=_("Start Of Treatment"), required=True
    )
    course_completed = fields.Boolean(
        string=_("Course Completed")
    )
    doctor = fields.Many2one(
        'medical.physician',
        string=_("Physician")
    )
    indication = fields.Many2one(
        'medical.pathology',
        string=_("Indication")
    )
    end_treatment = fields.Datetime(
        string=_("End Of Treatment"), required=True
    )
    discontinued = fields.Boolean(
        string=_("Discontinued")
    )
    form = fields.Many2one(
        'medical.drug.form',
        string=_("Form")
    )
    route = fields.Many2one(
        'medical.drug.route',
        string=_("Administration Route")
    )
    dose = fields.Float(
        string=_("Dose")
    )
    qty = fields.Integer(
        string=_("X")
    )
    dose_unit = fields.Many2one(
        'medical.dose.unit',
        string=_("Dose Unit")
    )
    duration = fields.Integer(
        string=_("Treatment Duration")
    )
    duration_period = fields.Selection(
        selection=DURATION_PERIOD,
        string=_("Treatment Period")
    )
    common_dosage = fields.Many2one(
        'medical.medication.dosage',
        string=_("Frequency"))
    admin_times = fields.Char(
        string=_("Admin Hours")
    )
    frequency = fields.Integer(
        string=_("Frequency")
    )
    frequency_unit = fields.Selection(
        selection=FREQUENCY_UNIT,
        string=_("Unit")
    )
    notes = fields.Text(
        string=_("Notes")
    )
    new_born_id = fields.Many2one(
        'medical.newborn', string=_("Newborn")
    )
