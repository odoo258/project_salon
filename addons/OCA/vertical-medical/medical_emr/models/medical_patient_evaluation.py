# -*- coding: utf-8 -*-
###############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2004-TODAY Tech-Receptives(<http://www.techreceptives.com>)
#    Special Credit and Thanks to Thymbra Latinoamericana S.A.
#    Ported to 8.0 by Dave Lasley - LasLabs (https://laslabs.com)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from odoo import fields, models


class MedicalPatientEvaluation(models.Model):
    _name = 'medical.patient.evaluation'
    _rec_name = 'patient_id'
    patient_id = fields.Many2one('medical.patient', 'Patient')
    information_source = fields.Char(
        size=256, string='Source',
        help="Source of" "Information, eg : Self, relative, friend ..."
    )
    info_diagnosis = fields.Text(
        string='Presumptive Diagnosis: Extra Info')
    is_disoriented = fields.Boolean(
        string='Orientation',
        help='Check this box if the patient is disoriented in time and/or'
        ' space'
    )
    weight = fields.Float(string='Weight',
                           help='Weight in Kilos')
    evaluation_type = fields.Selection([
        ('a', 'Ambulatory'),
        ('e', 'Emergency'),
        ('i', 'Inpatient'),
        ('pa', 'Pre-arranged appointment'),
        ('pc', 'Periodic control'),
        ('p', 'Phone call'),
        ('t', 'Telemedicine'),
    ], string='Type')
    is_malnutritious = fields.Boolean(
        string='Malnutrition',
        help='Check this box if the patient show signs of malnutrition. If'
        ' associated  to a disease, please encode the correspondent'
        ' disease on the patient disease history. For example, Moderate'
        ' protein-energy malnutrition, E44.0 in ICD-10 encoding'
    )
    action_ids = fields.One2many('medical.directions',
                                  'evaluation_id', string='Procedures',
                                  help='Procedures / Actions to take')
    height = fields.Float(string='Height',
                           help='Height in centimeters, eg 175')
    is_dehydrated = fields.Boolean(
        string='Dehydration',
        help='Check this box if the patient show signs of dehydration. If'
        ' associated  to a disease, please encode the correspondent'
        ' disease on the patient disease history. For example,'
        ' Volume Depletion, E86 in ICD-10 encoding'
    )
    tag = fields.Integer(
        string='Last TAGs',
        help='Triacylglycerol(triglicerides) level. Can be approximative'
    )
    is_tremor = fields.Boolean(
        string='Tremor',
        help='Check this box is the patient shows signs of tremors',
    )
    present_illness = fields.Text(string='Present Illness')
    evaluation_id = fields.Many2one(
        'medical.appointment', string='Appointment',
        help='Enter or select the date / ID of the appointment related to'
        ' this evaluation'
    )
    evaluation_date = fields.Datetime(
        related='evaluation_id', string='Evaluation Date',
        readonly=True)
    evaluation_start = fields.Datetime(string='Start', required=True)
    loc = fields.Integer(string='Level of Consciousness')
    user_id = fields.Many2one('res.users', string='Last Changed by',
                               readonly=True)
    mood = fields.Selection([
        ('n', 'Normal'),
        ('s', 'Sad'),
        ('f', 'Fear'),
        ('r', 'Rage'),
        ('h', 'Happy'),
        ('d', 'Disgust'),
        ('e', 'Euphoria'),
        ('fl', 'Flat'),
    ], string='Mood'),
    doctor_id = fields.Many2one('medical.physician', string='Doctor',
                                 readonly=True)
    is_incognizant = fields.Boolean(
        string='Knowledge of Current Events',
        help='Check this box if the patient can not respond to public'
        ' notorious events')
    next_evaluation_id = fields.Many2one('medical.appointment',
                                          string='Next Appointment',)
    signs_and_symptoms_ids = fields.One2many(
        'medical.signs_and_symptoms', 'evaluation_id',
        string='Signs and Symptoms',
        help="Enter the Signs and Symptoms for the patient in this"
        " evaluation."
    )
    loc_motor = fields.Selection([
        ('1', 'Makes no movement'),
        ('2', 'Extension to painful stimuli - decerebrate response -'),
        ('3',
         'Abnormal flexion to painful stimuli (decorticate response)'),
        ('4', 'Flexion / Withdrawal to painful stimuli'),
        ('5', 'Localizes painful stimuli'),
        ('6', 'Obeys commands'),
    ], string='Glasgow - Motor')
    is_reliable_info = fields.Boolean(
        string='Reliable', default=True,
        help="Uncheck this option"
        "if the information provided by the source seems not reliable"
    )
    systolic = fields.Integer(string='Systolic Pressure')
    vocabulary = fields.Boolean(
        string='Vocabulary',
        help='Check this box if the patient lacks basic intellectual'
        ' capacity, when she/he can not describe elementary objects'
    )
    is_catatonic = fields.Boolean(
        string='Catatonic',
        help='Check this box if the patient is unable to make voluntary'
        'movements'
    )
    hip = fields.Float(string='Hip',
                        help='Hip circumference in centimeters, eg 100')
    is_forgetful = fields.Boolean(
        string='Memory',
        help='Check this box if the patient has problems in short or long'
        ' term memory'
    )
    is_abstracting = fields.Boolean(
        string='Abstraction',
        help='Check this box if the patient presents abnormalities in'
        ' abstract reasoning'
    )
    referred_from_id = fields.Many2one(
        'medical.physician', string='Derived/Referred from',
        help='Physician who derived/referred the case')
    specialty_id = fields.Many2one('medical.specialty',
                                    string='Specialty',)
    loc_verbal = fields.Selection([
        ('1', 'Makes no sounds'),
        ('2', 'Incomprehensible sounds'),
        ('3', 'Utters inappropriate words'),
        ('4', 'Confused, disoriented'),
        ('5', 'Oriented, converses normally'),
    ], string='Glasgow - Verbal'),
    glycemia = fields.Float(
        string='Glycemia',
        help='Last blood glucose level. Can be approximative.'
    )
    head_circumference = fields.Float(string='Head Circumference',
                                       help='Head circumference')
    bmi = fields.Float(string='Body Mass Index')
    respiratory_rate = fields.Integer(
        string='Respiratory Rate',
        help='Respiratory rate expressed in breaths per minute'
    )
    referred_to_id = fields.Many2one(
        'medical.physician', string='Derived/Referred to',
        help='Physician to whom escalate / refer the case'
    )
    hba1c = fields.Float(
        string='Glycated Hemoglobin',
        help='Last Glycated Hb level. Can be approximative.'
    )
    is_violent = fields.Boolean(
        string='Violent Behaviour',
        help='Check this box if the patient is agressive or violent at the'
        ' moment'
    )
    directions = fields.Text(string='Plan')
    evaluation_summary = fields.Text(string='Evaluation Summary')
    cholesterol_total = fields.Integer(string='Last Cholesterol')
    diagnostic_hypothesis_id = fields.One2many(
        'medical.diagnostic_hypothesis',
        'evaluation_id', string='Hypotheses / DDx',
        help='Presumptive Diagnosis. If no diagnosis can be made'
        ', encode the main sign or symptom.')
    judgment = fields.Boolean(
        string='Jugdment',
        help='Check this box if the patient can not interpret basic'
        ' scenario solutions'
    )
    temperature = fields.Float(string='Temperature',
                                help='Temperature in celcius')
    osat = fields.Integer(string='Oxygen Saturation',
                           help='Oxygen Saturation(arterial).')
    secondary_condition_ids = fields.One2many(
        'medical.secondary_condition', 'evaluation_id',
        string='Secondary Conditions',
        help="Other, Secondary conditions found on the patient")
    evaluation_endtime = fields.Datetime(string='End', required=True)
    notes = fields.Text(string='Notes')
    calculation_ability = fields.Boolean(
        string='Calculation Ability',
        help='Check this box if the patient can not do simple arithmetic'
        ' problems'
    )
    bpm = fields.Integer(string='Heart Rate',
                          help='Heart rate expressed in beats per minute')
    chief_complaint = fields.Char(size=256, string='Chief Complaint',
                                   required=True,
                                   help='Chief Complaint')
    loc_eyes = fields.Selection([
        ('1', 'Does not Open Eyes'),
        ('2', 'Opens eyes in response to painful stimuli'),
        ('3', 'Opens eyes in response to voice'),
        ('4', 'Opens eyes spontaneously'),
    ], string='Glasgow - Eyes'),
    abdominal_circ = fields.Float(string='Waist')
    not_perceiving = fields.Boolean(
        string='Object Recognition',
        help='Check this box if the patient suffers from any sort of'
        ' gnosia disorders, such as agnosia, prosopagnosia ...'
    )
    diagnosis_id = fields.Many2one('medical.pathology',
                                    string='Presumptive Diagnosis',)
    whr = fields.Float(string='WHR', help='Waist to hip ratio')
    ldl = fields.Integer(
        string='Last LDL',
        help='Last LDL Cholesterol reading. Can be approximative'
    )
    notes_complaint = fields.Text(string='Complaint details')
    hdl = fields.Integer(string='Last HDL')
    diastolic = fields.Integer(string='Diastolic Pressure')
