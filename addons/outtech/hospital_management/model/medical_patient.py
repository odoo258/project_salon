# -*- coding: utf-8 -*-
##############################################################################
#
#    This module uses OpenERP, Open Source Management Solution Framework.
#    Copyright (C) 2014-Today BrowseInfo (<http://www.browseinfo.in>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################
from openerp import api, fields, models, _
from datetime import datetime
from dateutil.relativedelta import relativedelta


class medical_patient_cage(models.Model):
    _name = 'medical.patient.cage'

    @api.one
    @api.onchange('cage_c', 'cage_a', 'cage_g', 'cage_e')
    def get_score(self):
        self.cage_score = int(self.cage_c) + int(self.cage_a) + int(self.cage_g) + int(self.cage_e)

    patient_id = fields.Many2one('medical.patient')
    evaluation_date = fields.Datetime()
    cage_c = fields.Boolean(default=False)
    cage_a = fields.Boolean(default=False)
    cage_g = fields.Boolean(default=False)
    cage_e = fields.Boolean(default=False)
    cage_score = fields.Integer('Cage Score', default=0)


class medical_patient_menstrual_history(models.Model):
    _name = 'medical.patient.menstrual.history'

    patient_id = fields.Many2one('medical.patient', 'Patient')

    evoultion_date = fields.Date('Date')
    lmp = fields.Integer('LMP', required=True)
    lmp_length = fields.Integer('LMP Length', required=True)
    is_regular = fields.Boolean('IS Regular')
    dysmenorrhea = fields.Boolean('Dysmenorrhea')
    frequency = fields.Selection([('amenorrhea', 'Amenorrhea'),
                                  ('oligomenorrhea', 'Oligomenorrhea'),
                                  ('eumenorrhea', 'Eumenorrhea'),
                                  ('pollymenohea', 'Pollymenohea')])
    volume = fields.Selection([('hopomenorrhea', 'hopomenorrhea'),
                               ('normal', 'Normal'),
                               ('menorrhagia', 'Menorrhagia')])


class medical_patient_mammography_history(models.Model):
    _name = 'medical.patient.mammography.history'

    patient_id = fields.Many2one('medical.patient', 'Patient')
    evolution_id = fields.Many2one('medical.patient.evaluation', 'Evaluation')
    evolution_date = fields.Date('Date')
    last_mamography_date = fields.Date('Date')
    result = fields.Selection([('normal', 'Normal'), ('abnormal', 'Abnormal')])
    remark = fields.Char('Comments')


class medical_patient_pap_history(models.Model):
    _name = 'medical.patient.pap.history'

    patient_id = fields.Many2one('medical.patient', 'Patient')
    evolution_id = fields.Many2one('medical.patient.evaluation', 'Evaluation')
    evolution_date = fields.Datetime('Evaluation Date')
    result = fields.Selection([('negative', 'Negative'),
                               ('c1', 'ASC-US'),
                               ('c2', 'ASC-H'),
                               ('g1', 'ASG'),
                               ('c3', 'LSIL'),
                               ('c4', 'HISL'),
                               ('g4', 'AIS')], 'Result')
    remark = fields.Char('Remark')


class medical_patient_coloscopy_history(models.Model):
    _name = 'medical.patient.colposcopy.history'

    patient_id = fields.Many2one('medical.patient', 'Patient')
    evolution_id = fields.Many2one('medical.patient.evaluation', 'Evaluation')
    result = fields.Selection([('negative', 'Negative'),
                               ('c1', 'ASC-US'),
                               ('c2', 'ASC-H'),
                               ('g1', 'ASG'),
                               ('c3', 'LSIL'),
                               ('c4', 'HISL'),
                               ('g4', 'AIS')], 'Result')
    remark = fields.Char('Remark')
    evolution_date = fields.Datetime('Evaluation Date')


class medical_patient_prental_evolution(models.Model):
    _name = 'medical.patient.prental.evoultion'

    pregnency_id = fields.Many2one('medical.patient.pregnency', )
    evoultion_date = fields.Date('Date', required=True)
    gestational_weeks = fields.Integer('Gestational Weeks', required=True)
    hypertansion = fields.Boolean('Hypertension')
    preclampsia = fields.Boolean('Prclampsia')
    overwieght = fields.Boolean('Overweight')
    diabetes = fields.Boolean('Diabetes')
    placenta_previa = fields.Boolean('Placenta Previa')
    invasive_placentation = fields.Selection([('normal_decidua', 'Normal Decidua'),
                                              ('accreta', 'Accreta'),
                                              ('increta', 'Increta'),
                                              ('percreta', 'Precreta')])
    vasa_previa = fields.Boolean('Vasa Previa')
    fundel_weight = fields.Integer('Fundel Weight')
    fetus_heart_rate = fields.Integer('Fetus Heart Rate')
    efw = fields.Integer('EFW')
    bpd = fields.Integer('BPD')
    hc = fields.Integer('HC')
    ac = fields.Integer('AC')
    fl = fields.Integer('FL')


class puerperium_monitor(models.Model):
    _name = 'medical.puerperium.monitor'

    pregnency_id = fields.Many2one('medical.patient.pregnency')
    date = fields.Datetime('Date And Time')
    systolic_pressure = fields.Integer('Systolic Pressure')
    diastolic_pressure = fields.Integer('Diastolic Pressure')
    heart_freq = fields.Integer('Heart Frequency')
    temprature = fields.Integer('Temperature')
    fundal_height = fields.Integer('Fundal Height')
    lochia_amount = fields.Selection([('n', 'Normal'), ('a', 'Abudant'), ('h', 'Hemorrhage'), ], 'Lochia amount')
    lochia_color = fields.Selection([('r', 'Rubra'), ('s', 'Serosa'), ('a', 'Alba')], 'Loicha Color')
    loicha_order = fields.Selection([('n', 'Normal'), ('o', 'Offensive')], 'Loicha Order')


class medical_perinatal_monitor(models.Model):
    _name = 'medical.perinatal.monitor'

    medical_perinatal_id = fields.Many2one('medical.perinatal.monitor')
    date = fields.Date('Date')
    systolic = fields.Integer('Systolic Pressure')
    diastolic = fields.Integer('Diastolic Pressure')
    mothers_heart_freq = fields.Integer('Mothers Heart Freq')
    consentration = fields.Integer('Consentration')
    cervix_dilation = fields.Integer('Cervix Dilation')
    fundel_height = fields.Integer('Fundel Height')
    fetus_presentation = fields.Selection([('n', 'Correct'),
                                           ('o', 'Occiput /Cephalic Postrior'),
                                           ('fb', 'Frank Breech'),
                                           ('cb', 'Complete Breech'),
                                           ('tl', 'Transverse Lie'),
                                           ('fu', 'Footling Lie')], 'Fetus Presentation')
    f_freq = fields.Integer('Fetus Heart Frequency')
    bleeding = fields.Boolean('Bleeding')
    meconium = fields.Boolean('Meconium')
    notes = fields.Char('Notes')


class medical_perinatal(models.Model):
    _name = 'medical.preinatal'

    pregnency_id = fields.Many2one('medical.patient.pregnency', 'Pregnancy', )
    gestational_weeks = fields.Integer('Gestational weeks')
    admission_date = fields.Date('Admission Date')
    code = fields.Char('Code')
    labour_mode = fields.Selection([('n', 'Normal'), ('i', 'Induced'), ('c', 'C-Section')], 'Labour Mode')
    fetus_presentation = fields.Selection([('n', 'Correct'),
                                           ('o', 'Occiput /Cephalic Postrior'),
                                           ('fb', 'Frank Breech'),
                                           ('cb', 'Complete Breech'),
                                           ('tl', 'Transverse Lie'),
                                           ('fu', 'Footling Lie')], 'Fetus Presentation')
    monitor_ids = fields.One2many('medical.perinatal.monitor', 'medical_perinatal_id')
    dystocia = fields.Boolean('Dystocia')
    episiotomy = fields.Boolean('Episiotomy')
    lacerations = fields.Selection([('p', 'Perinial'),
                                    ('v', 'Vaginal'),
                                    ('c', 'Cervical'),
                                    ('bl', 'Broad Ligament'),
                                    ('vl', 'Vulvar'),
                                    ('r', 'Rectal'),
                                    ('br', 'Blader'),
                                    ('u', 'Ureteral'), ], 'Lacerations')

    hematoma = fields.Selection([('v', 'Vaginal'), ('vl', 'Vulvar'), ('r', 'Retroperitional')], 'Hematoma')
    plancenta_incomplete = fields.Boolean('Incomplete Placenta')
    retained_placenta = fields.Boolean('Retained Placenta')
    abruptio_placentae = fields.Boolean('Abruptio Placentae')

    notes = fields.Text('Notes')


class medical_patient_disease(models.Model):
    _name = "medical.patient.disease"
    _rec_name = 'patient_id'

    pathology_id = fields.Many2one('medical.pathology', 'Disease', required=True)
    disease_severity = fields.Selection([('1_mi', 'Mild'),
                                         ('2_mo', 'Moderate'),
                                         ('3_sv', 'Severe')], 'Severity')
    status = fields.Selection([('c', 'Chronic'),
                               ('s', 'Status quo'),
                               ('h', 'Healed'),
                               ('i', 'Improving'),
                               ('w', 'Worsening')], 'Status of the disease')
    is_infectious = fields.Boolean('Infectious Disease')
    is_active = fields.Boolean('Active disease')
    short_comment = fields.Char('Remarks')
    diagnosis_date = fields.Date('Date of Diagnosis')
    healed_date = fields.Date('Healed')
    doctor_id = fields.Many2one('medical.physician', 'Physician')
    is_allergic = fields.Boolean('Allergic Disease')
    allergy_type = fields.Selection([('da', 'Drag Allergy'),
                                     ('fa', 'Food Allergy'),
                                     ('ma', 'Misc Allergy'),
                                     ('mc', 'Misc Contraindication')], 'Allergy type')
    pregnancy_warning = fields.Boolean('Pregnancy warning')
    week_of_pregnancy = fields.Integer('Contracted in pregnancy week #')
    is_on_treatment = fields.Boolean('Currently on Treatment')
    treatment_description = fields.Char('Treatment Description')
    date_start_treatment = fields.Date('Start of treatment')
    date_stop_treatment = fields.Date('End of treatment')
    psc_cod_id = fields.Many2one('medical.procedure', 'Code')
    patient_id = fields.Many2one('medical.patient', string="Patient")
    new_born_id = fields.Many2one('medical.newborn', string="Newborn")
    extra_info = fields.Text('info')


class medical_patient_pregnency(models.Model):
    _name = 'medical.patient.pregnency'

    gravida = fields.Integer('Pregnancy #')
    lmp = fields.Integer('LMP')
    pdd = fields.Date('Pregnency  Due Date')
    patient_id = fields.Many2one('medical.patient', 'Patient')
    current_pregnency = fields.Boolean('Current Pregnency')
    medical_patient_evolution_prental_ids = fields.One2many('medical.patient.prental.evoultion', 'pregnency_id',
                                                            'Patient Perinatal Evaluations')
    medical_perinatal_ids = fields.One2many('medical.preinatal', 'pregnency_id', 'Medical Perinatal ')
    puerperium_perental_ids = fields.One2many('medical.puerperium.monitor', 'pregnency_id', 'Puerperium Monitor')
    fetuses = fields.Boolean('Fetuses')
    monozygotic = fields.Boolean('Monozygotic')
    igur = fields.Selection([('s', 'Symmetric'), ('a', 'Asymmetric')], 'IGUR')
    warn = fields.Boolean('Warning')
    result = fields.Char('Result')
    pregnancy_end_date = fields.Date('Pregnancy End Date')
    pregnancy_end_result = fields.Char('Pregnancy End Result')


class MedicalPatient(models.Model):
    _name = 'medical.patient'

    def _get_is_salon(self):
        company = self.env['res.company']._company_default_get()
        self.is_salon = company[0].salon_allowed

    @api.multi
    def print_report(self):
        self.ensure_one()
        self.sent = True
        return self.env['report'].get_action(self, 'hospital_management.report_patient_card')

    patient_id = fields.Many2one('res.partner', string="Owner", required=False)
    owner_id = fields.Many2one('res.partner', string="Owner", required=True)
    name = fields.Char(string='Name', required=True)
    last_name = fields.Char('Last Name')
    dob = fields.Date(string="Date of Birth")
    sex = fields.Selection([('m', 'Male'), ('f', 'Female')], string="Sex")
    age = fields.Char(
        string="Patient Age",
        compute='_compute_age'
    )
    blood_type = fields.Selection([('A', 'A'), ('B', 'B'), ('AB', 'AB'), ('O', 'O'), ])
    critical_info = fields.Text(string="Patient Critical Information")
    photo = fields.Binary(string="Picture", attachment=True)
    ethnic_group = fields.Many2one('medical.ethnicity', string="Ethnic Group")
    deceased = fields.Boolean(string='Deceased')
    dod = fields.Datetime(string="Date of Death")
    cod = fields.Char(string='Cause of Death')
    microchip_code = fields.Char(string='Microchip Code')
    current_insurance = fields.Many2one('medical.insurance', string="Insurance")
    patient_status = fields.Char(string="Hospitalization Status", readonly=True)
    diseases = fields.One2many('medical.patient.disease', 'patient_id')
    psc = fields.One2many('medical.patient.psc', 'patient_id')
    general_info = fields.Text(string="Info")
    cage = fields.One2many('medical.patient.cage', 'patient_id')
    fertile = fields.Boolean('Fertile')
    menarche = fields.Integer('Menarche age')
    menopausal = fields.Boolean('Menopausal')
    menopause = fields.Integer('Menopause age')
    menstrual_history = fields.One2many('medical.patient.menstrual.history', 'patient_id')
    breast_self_examination = fields.Boolean('Breast self-examination')
    mammography = fields.Boolean('Mammography')
    pap_test = fields.Boolean('PAP test')
    last_pap_test = fields.Date('Last PAP test')
    colposcopy = fields.Boolean('Colposcopy')
    mammography_history = fields.One2many('medical.patient.mammography.history', 'patient_id')
    pap_history = fields.One2many('medical.patient.pap.history', 'patient_id')
    colposcopy_history = fields.One2many('medical.patient.colposcopy.history', 'patient_id')
    pregnancies = fields.Integer('Pregnancies')
    premature = fields.Integer('Premature')
    stillbirths = fields.Integer('Stillbirths')
    abortions = fields.Integer('Abortions')
    pregnancy_history = fields.One2many('medical.patient.pregnency', 'patient_id')
    genetic_risks = fields.Many2many('medical.genetic.risk')
    family_history = fields.Many2many('medical.family.disease')
    perinatal = fields.Many2many('medical.preinatal')
    ex_alcoholic = fields.Boolean('Ex alcoholic')
    currently_pregnant = fields.Boolean('Currently Pregnant')
    born_alive = fields.Integer('Born Alive')
    gpa = fields.Char('GPA')
    colposcopy_last = fields.Date('Last colposcopy')
    mammography_last = fields.Date('Last mammography')
    works = fields.Boolean('Works')
    notes = fields.Text(string="Extra info")
    trash = fields.Boolean('Trash recollection')
    fertile = fields.Boolean('Fertile')
    menarche_age = fields.Integer('Menarche age')
    menopausal = fields.Boolean('Menopausal')
    pap_test_last = fields.Date('Last PAP Test')
    colposcopy = fields.Boolean('Colpscopy')
    gravida = fields.Integer('Pregnancies')
    # medical_vaccination = fields.One2many('medical.vaccination','medical_patient_vaccines_id')
    medical_appointments = fields.One2many('medical.appointment', 'patient_id', string='Appointments')
    lastname = fields.Char('Last Name')
    report_date = fields.Date('Date', default=fields.Date.context_today)
    # medication_ids = fields.One2many('medical.patient.medication1','medical_patient_medication_id')
    # medications = fields.One2many('medical.patient.medication','medical_patient_medication_id',string='Medication')
    deaths_2nd_week = fields.Integer('Deceased after 2nd week')
    deaths_1st_week = fields.Integer('Deceased after 1st week')
    full_term = fields.Integer('Full Term')
    especie_id = fields.Many2one(
        'pet.especie', string="Especie"
    )
    color_id = fields.Many2one(
        'pet.color', string="Color"
    )
    hair_id = fields.Many2one(
        'pet.hair', string="Hair"
    )
    admission_ids = fields.One2many(
        'medical.inpatient.registration', 'patient',
        string="Admissions"
    )
    salon_order_ids = fields.One2many(
        'salon.order', 'patient_id', 'Salon Orders'
    )
    prescription_ids = fields.One2many(
        'medical.prescription.order', 'patient_id', 'Salon Orders'
    )
    map_ids = fields.One2many(
        'medical.map', 'patient_id', 'Maps'
    )
    is_salon = fields.Boolean(
        string="Is Salon", compute='_get_is_salon'
    )
    _sql_constraints = [
        ('microchip_code', 'unique(microchip_code)', _("There is already another pet with this microchip"))
    ]

    @api.depends('dob')
    def _compute_age(self):
        if self.dob:
            dt = self.dob
            d1 = datetime.strptime(dt, "%Y-%m-%d").date()
            d2 = datetime.today()
            rd = relativedelta(d2, d1)
            value = u"{year} {year_str}, {month} {month_str}, {day} {day_str}".format(
                year=rd.years, year_str=_("Year(s)"),
                month=rd.months, month_str=_("Month(s)"),
                day=rd.days, day_str=_("Day(s)")
            )
            self.age = value
        else:
            self.age = False
