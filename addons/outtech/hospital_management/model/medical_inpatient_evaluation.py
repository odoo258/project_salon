# coding=utf-8
# Author: Christian Douglas <christian.douglas.alcantara@gmail.com>
from odoo import models, fields, _


class MedicalInpatientEvaluation(models.Model):
    _name = 'medical.inpatient.evaluation'
    _rec_name = 'patient_id'

    EVALUATION_TYPES = [
        ('a', _("Ambulatory")),
        ('e', _("Emergency")),
        ('i', _("Inpatient")),
        ('pa', _("Pre-arranged appointment")),
        ('pc', _("Periodic control")),
        ('p', _("Phone call")),
        ('t', _("Telemedicine")),
    ]
    MOODS = [
        ('n', _("Normal")),
        ('s', _("Sad")),
        ('f', _("Fear")),
        ('r', _("Rage")),
        ('h', _("Happy")),
        ('d', _("Disgust")),
        ('e', _("Euphoria")),
        ('fl', _("Flat")),
    ]
    LOC_EYES = [
        ('1', _("Does not Open Eyes")),
        ('2', _("Opens eyes in response to painful stimuli")),
        ('3', _("Opens eyes in response to voice")),
        ('4', _("Opens eyes spontaneously"))
    ]
    LOC_VERBAL = [
        ('1', _("Make no sounds")),
        ('2', _("Incomprehensible Sounds")),
        ('3', _("Utters inappropriate words")),
        ('4', _("Confused,disoriented")),
        ('5', _("Oriented, converses normally")),
    ]
    LOC_MOTOR = [
        ('1', _("Make no movement")),
        ('2', _("Extension to painful stimuli decerebrate response")),
        ('3', _("Abnormal flexion to painful stimuli decerebrate response")),
        ('4', _("Flexion/Withdrawal to painful stimuli")),
        ('5', _("Localizes painful stimuli")),
        ('6', _("Obeys commands")),
    ]
    VISIT_TYPE = [
        ('new', _("New Health Condition")),
        ('follow', _("FollowUp")),
        ('chronic', _("Chronic Condition ChechUp")),
        ('child', _("Well Child Visit")),
        ('women', _("Well Woman Visit")),
        ('man', _("Well Man Visit"))
    ]
    URGENCY = [
        ('a', _("Normal")),
        ('b', _("Urgent")),
        ('c', _("Medical Emergency"))
    ]
    # ORM Fields
    patient_id = fields.Many2one(
        'res.partner',
        string=_("Patient"), required=True
    )
    medical_inpatient_registration_id = fields.Many2one(
        'medical.inpatient.registration',
        string=_("Inpatiente Registration"), required=True
    )
    start_evaluation = fields.Datetime(
        string=_("Start Evaluation")
    )
    physicians_id = fields.Many2one(
        comodel_name='res.partner',
        string=_("Doctor")
    )
    end_evaluation = fields.Datetime(
        string=_("End of Evaluation")
    )
    evaluation_type = fields.Selection(
        selection=EVALUATION_TYPES,
        string=_("Type")
    )
    chief_complaint = fields.Char(
        string=_("Chief Complaint")
    )
    information_source = fields.Char(
        string=_("Source")
    )
    reliable_info = fields.Boolean(
        string=_("Reliable")
    )
    present_illness = fields.Text(
        string="Present Illness"
    )
    weight = fields.Float(
        string=_("Weight (kg)"),
        help=_("Weight in Kilos")
    )
    height = fields.Float(
        string=_("Height (cm)")
    )
    abdominal_circ = fields.Float(
        string=_("Abdominal Circumference")
    )
    hip = fields.Float(
        string=_("Hip")
    )
    bmi = fields.Float(
        string=_("Body Mass Index")
    )
    whr = fields.Float(
        string=_("WHR")
    )
    head_circumference = fields.Float(
        string=_("Head Circumference")
    )
    malnutrition = fields.Boolean(
        string=_("Malnutrition")
    )
    dehydration = fields.Boolean(
        string=_("Dehydration")
    )
    tag = fields.Integer(
        string=_("Last TAGs"),
        help=_("Triacylglycerol(triglicerides) level. Can be approximative")
    )
    is_tremor = fields.Boolean(
        string=_("Tremor"),
        help=_("Check this box is the patient shows signs of tremors"),
    )
    mood = fields.Selection(
        selection=MOODS,
        string=_("Mood")
    )
    specialty_id = fields.Many2one(
        comodel_name=_("medical.speciality"),
        string='Specialty'
    )
    glycemia = fields.Float(
        string=_("Glycemia"),
        help=_("Last blood glucose level. Can be approximative.")
    )
    evaluation_summary = fields.Text(
        string=_("Evaluation Summary")
    )
    temperature = fields.Float(
        string=_("Temperature (celsius)"),
        help=_("Temperature in celcius")
    )
    osat = fields.Integer(
        string=_("Oxygen Saturation"),
        help=_("Oxygen Saturation(arterial).")
    )
    bpm = fields.Integer(
        string=_("Heart Rate"),
        help=_("Heart rate expressed in beats per minute")
    )
    loc_eyes = fields.Selection(
        selection=LOC_EYES,
        string=_("Glasgow - Eyes")
    )
    loc_verbal = fields.Selection(
        selection=LOC_VERBAL,
        string=_("Glasgow - Verbal")
    )
    loc_motor = fields.Selection(
        selection=LOC_MOTOR,
        string=_("Glasgow - Motor")
    )
    violent = fields.Boolean(
        string=_("Violent Behaviour")
    )
    orientation = fields.Boolean(
        string=_("Orientation")
    )
    memory = fields.Boolean(
        string=_("Memory")
    )
    knowledge_current_events = fields.Boolean(
        string=_("Knowledge of Current Events")
    )
    judgment = fields.Boolean(
        string=_("Jugdment")
    )
    symptom_proctorrhagia = fields.Boolean(
        string=_("Polyphagia")
    )
    abstraction = fields.Boolean(
        string=_("Abstraction")
    )
    vocabulary = fields.Boolean(
        string=_("Vocabulary")
    )
    symptom_pain = fields.Boolean(
        string=_("Pain")
    )
    symptom_pain_intensity = fields.Integer(
        string=_("Pain intensity")
    )
    symptom_arthralgia = fields.Boolean(
        string=_("Arthralgia")
    )
    symptom_abdominal_pain = fields.Boolean(
        string=_("Abdominal Pain")
    )
    symptom_thoracic_pain = fields.Boolean(
        string=_("Thoracic Pain")
    )
    symptom_pelvic_pain = fields.Boolean(
        string=_("Pelvic Pain")
    )
    symptom_hoarseness = fields.Boolean(
        string=_("Hoarseness")
    )
    symptom_sore_throat = fields.Boolean(
        string=_("Sore throat")
    )
    symptom_ear_discharge = fields.Boolean(
        string=_("Ear Discharge")
    )
    symptom_chest_pain_excercise = fields.Boolean(
        string=_("Chest Pain on excercise only")
    )
    symptom_astenia = fields.Boolean(
        string=_("Astenia")
    )
    symptom_weight_change = fields.Boolean(
        string=_("Sudden weight change")
    )
    symptom_hemoptysis = fields.Boolean(
        string=_("Hemoptysis")
    )
    symptom_epistaxis = fields.Boolean(
        string=_("Epistaxis")
    )
    symptom_rinorrhea = fields.Boolean(
        string=_("Rinorrhea")
    )
    symptom_vomiting = fields.Boolean(
        string=_("Vomiting")
    )
    symptom_polydipsia = fields.Boolean(
        string=_("Polydipsia")
    )
    symptom_polyuria = fields.Boolean(
        string=_("Polyuria")
    )
    symptom_vesical_tenesmus = fields.Boolean(
        string=_("Vesical Tenesmus")
    )
    symptom_dysuria = fields.Boolean(
        string=_("Dysuria")
    )
    symptom_myalgia = fields.Boolean(
        string=_("Myalgia")
    )
    symptom_cervical_pain = fields.Boolean(
        string=_("Cervical Pain")
    )
    symptom_lumbar_pain = fields.Boolean(
        string=_("Lumbar Pain")
    )
    symptom_headache = fields.Boolean(
        string=_("Headache")
    )
    symptom_odynophagia = fields.Boolean(
        string=_("Odynophagia")
    )
    symptom_otalgia = fields.Boolean(
        string=_("Otalgia")
    )
    symptom_chest_pain = fields.Boolean(
        string=_("Chest Pain")
    )
    symptom_orthostatic_hypotension = fields.Boolean(
        string=_("Orthostatic hypotension")
    )
    symptom_anorexia = fields.Boolean(
        string=_("Anorexia")
    )
    symptom_abdominal_distension = fields.Boolean(
        string=_("Abdominal Distension")
    )
    symptom_hematemesis = fields.Boolean(
        string=_("Hematemesis")
    )
    symptom_gingival_bleeding = fields.Boolean(
        string=_("Gingival Bleeding")
    )
    symptom_nausea = fields.Boolean(
        string=_("Nausea")
    )
    symptom_dysphagia = fields.Boolean(
        string=_("Dysphagia")
    )
    symptom_polyphagia = fields.Boolean(
        string=_("Polyphagia")
    )
    symptom_nocturia = fields.Boolean(
        string=_("Nocturia")
    )
    symptom_pollakiuria = fields.Boolean(
        string=_("Pollakiuiria")
    )
    symptom_mood_swings = fields.Boolean(
        string=_("Mood Swings")
    )
    symptom_pruritus = fields.Boolean(
        string=_("Pruritus")
    )
    symptom_disturb_sleep = fields.Boolean(
        string=_("Disturbed Sleep")
    )
    symptom_orthopnea = fields.Boolean(
        string=_("Orthopnea")
    )
    symptom_paresthesia = fields.Boolean(
        string=_("Paresthesia")
    )
    symptom_dizziness = fields.Boolean(
        string=_("Dizziness")
    )
    symptom_tinnitus = fields.Boolean(
        string=_("Tinnitus")
    )
    symptom_eye_glasses = fields.Boolean(
        string=_("Eye glasses")
    )
    symptom_diplopia = fields.Boolean(
        string=_("Diplopia")
    )
    symptom_dysmenorrhea = fields.Boolean(
        string=_("Dysmenorrhea")
    )
    symptom_metrorrhagia = fields.Boolean(
        string=_("Metrorrhagia")
    )
    symptom_vaginal_discharge = fields.Boolean(
        string=_("Vaginal Discharge")
    )
    symptom_diarrhea = fields.Boolean(
        string=_("Diarrhea")
    )
    symptom_rectal_tenesmus = fields.Boolean(
        string=_("Rectal Tenesmus")
    )
    symptom_sexual_dysfunction = fields.Boolean(
        string=_("Sexual Dysfunction")
    )
    symptom_stress = fields.Boolean(
        string=_("Stressed-out")
    )
    symptom_insomnia = fields.Boolean(
        string=_("Insomnia")
    )
    symptom_dyspnea = fields.Boolean(
        string=_("Dyspnea")
    )
    symptom_amnesia = fields.Boolean(
        string=_("Amnesia")
    )
    symptom_paralysis = fields.Boolean(
        string=_("Paralysis")
    )
    symptom_vertigo = fields.Boolean(
        string=_("Vertigo")
    )
    symptom_syncope = fields.Boolean(
        string=_("Syncope")
    )
    symptom_blurry_vision = fields.Boolean(
        string=_("Blurry vision")
    )
    symptom_photophobia = fields.Boolean(
        string=_("Photophobia")
    )
    symptom_amenorrhea = fields.Boolean(
        string=_("Amenorrhea")
    )
    symptom_menorrhagia = fields.Boolean(
        string=_("Menorrhagia")
    )
    symptom_urethral_discharge = fields.Boolean(
        string=_("Urethral Discharge")
    )
    symptom_constipation = fields.Boolean(
        string=_("Constipation")
    )
    symptom_melena = fields.Boolean(
        string=_("Melena")
    )
    symptom_xerostomia = fields.Boolean(
        string=_("Xerostomia")
    )
    calculation_ability = fields.Boolean(
        string=_("Calculation Ability")
    )
    object_recognition = fields.Boolean(
        string=_("Object Recognition")
    )
    praxis = fields.Boolean(
        string=_("Praxis")
    )
    edema = fields.Boolean(
        string=_("Edema")
    )
    petechiae = fields.Boolean(
        string=_("Petechiae")
    )
    acropachy = fields.Boolean(
        string=_("Acropachy")
    )
    miosis = fields.Boolean(
        string=_("Miosis")
    )
    cough = fields.Boolean(
        string=_("Cough")
    )
    arritmia = fields.Boolean(
        string=_("Arritmias")
    )
    heart_extra_sounds = fields.Boolean(
        string=_("Heart Extra Sounds")
    )
    ascites = fields.Boolean(
        string=_("Ascites")
    )
    bronchophony = fields.Boolean(
        string=_("Bronchophony")
    )
    cyanosis = fields.Boolean(
        string=_("Cyanosis")
    )
    hematoma = fields.Boolean(
        string=_("Hematomas")
    )
    nystagmus = fields.Boolean(
        string=_("Nystagmus")
    )
    mydriasis = fields.Boolean(
        string=_("Mydriasis")
    )
    palpebral_ptosis = fields.Boolean(
        string=_("Palpebral Ptosis")
    )
    heart_murmurs = fields.Boolean(
        string=_("Heart Murmurs")
    )
    jugular_engorgement = fields.Boolean(
        string=_("Tremor")
    )
    lung_adventitious_sounds = fields.Boolean(
        string=_("Lung Adventitious sounds")
    )
    increased_fremitus = fields.Boolean(
        string=_("Increased Fremitus")
    )
    jaundice = fields.Boolean(
        string=_("Jaundice")
    )
    breast_lump = fields.Boolean(
        string=_("Breast Lumps")
    )
    nipple_inversion = fields.Boolean(
        string=_("Nipple Inversion")
    )
    peau_dorange = fields.Boolean(
        string=_("Peau d orange")
    )
    hypotonia = fields.Boolean(
        string=_("Hypotonia")
    )
    masses = fields.Boolean(
        string=_("Masses")
    )
    goiter = fields.Boolean(
        string=_("Goiter")
    )
    xerosis = fields.Boolean(
        string=_("Xerosis")
    )
    decreased_fremitus = fields.Boolean(
        string=_("Decreased Fremitus")
    )
    lynphadenitis = fields.Boolean(
        string=_("Linphadenitis")
    )
    breast_asymmetry = fields.Boolean(
        string=_("Breast Asymmetry")
    )
    nipple_discharge = fields.Boolean(
        string=_("Nipple Discharge")
    )
    gynecomastia = fields.Boolean(
        string=_("Gynecomastia")
    )
    hypertonia = fields.Boolean(
        string=_("Hypertonia")
    )
    pressure_ulcers = fields.Boolean(
        string=_("Pressure Ulcers")
    )
    alopecia = fields.Boolean(
        string=_("Alopecia")
    )
    erithema = fields.Boolean(
        string=_("Erithema")
    )
    diagnosis_id = fields.Many2one(
        'medical.pathology',
        string=_("Presumptive Diagnosis")
    )
    visit_type = fields.Selection(
        selection=VISIT_TYPE,
        string=_("Visit")
    )
    urgency = fields.Selection(
        selection=URGENCY,
        string=_("Urgency")
    )
    systolic = fields.Integer(
        string=_("Systolic Pressure")
    )
    diastolic = fields.Integer(
        string=_("Diastolic Pressure")
    )
    respiratory_rate = fields.Integer(
        string="Respiratory Rate")

    signs_and_symptoms_ids = fields.One2many(
        'medical.signs.and.sympotoms', 'inpatient_evaluation_id',
        string=_("Signs and Symptoms")
    )
    hba1c = fields.Float(
        string=_("Glycated Hemoglobin")
    )
    cholesterol_total = fields.Integer(
        string=_("Last Cholesterol")
    )
    hdl = fields.Integer(
        string=_("Last HDL")
    )
    ldl = fields.Integer(
        string=_("Last LDL"),
        help=_("Last LDL Cholesterol reading. Can be approximative")
    )
    tags = fields.Integer(
        string=_("Last TAGs")
    )
    loc = fields.Integer(
        string=_("Level of Consciousness")
    )
    info_diagnosis = fields.Text(
        string=_("Information on Diagnosis")
    )
    directions = fields.Text(
        string=_("Treatment Plan")
    )
    user_id = fields.Many2one(
        comodel_name='res.users',
        string=_("Doctor user ID"), readonly=True
    )
    evaluation_date_id = fields.Many2one(
        colmodels_name='medical.appointment',
        string=_("Appointment Date")
    )
    next_evaluation_id = fields.Many2one(
        'medical.appointment',
        string=_("Next Appointment")
    )
    derived_from_id = fields.Many2one(
        'medical.physician',
        string=_("Derived from Doctor")
    )
    derived_to_id = fields.Many2one(
        'medical.physician',
        string=_("Derived to Doctor")
    )
    secondary_conditions_ids = fields.One2many(
        'medical.secondary_condition', 'inpatient_evaluation_id',
        string=_("Secondary Conditions")
    )
    diagnostic_hypothesis_ids = fields.One2many(
        'medical.diagnostic_hypotesis', 'inpatient_evaluation_id',
        string=_("Procedures")
    )
    action_ids = fields.One2many(
        'medical.directions', 'inpatient_evaluation_id',
        string=_("Procedures")
    )
