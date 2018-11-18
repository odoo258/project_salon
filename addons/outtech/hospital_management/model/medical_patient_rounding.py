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
from vobject.base import readOne

class medical_patient_rounding(models.Model):
    _name = "medical.patient.rounding"
    
    @api.onchange('right_pupil','left_pupil')
    def onchange_duration(self):
        if self.left_pupil == self.right_pupil:
            self.anisocoria = False
        else:
            self.anisocoria = True
    
    name = fields.Many2one('medical.inpatient.registration',string="Registration Code",required=True)
    health_professional = fields.Many2one('medical.physician',string="Health Professional",readonly=True)
    evaluation_start = fields.Datetime(string="Start",required=True)
    evaluation_end = fields.Datetime(string="End",required=True)
    environmental_assessment = fields.Char(string='Environment')
    icu_patient = fields.Boolean(string='ICU')
    warning = fields.Boolean(string='Warning')
    pain = fields.Boolean(string='Pain')
    potty = fields.Boolean(string='Potty')
    position = fields.Boolean(string='Position')
    proximity = fields.Boolean(string='Proximity')
    pump = fields.Boolean(string='Pumps')
    personal_needs = fields.Boolean(string='Personal Needs')
    temperature =fields.Float(string='Temperature')
    systolic = fields.Integer(string="Systolic Pressure")
    diastolic = fields.Integer(string='Diastolic Pressure')
    bpm = fields.Integer(string='Heart Rate')
    respiratory_rate = fields.Integer(string="Respiratory Rate")
    osat = fields.Integer(string="Oxygen Saturation")
    diuresis = fields.Integer(string="Diuresis")
    urinary_catheter = fields.Boolean(string="Urinary Catheter")
    glycemia = fields.Integer(string="Glycemia")
    depression = fields.Boolean(string="Depression Signs")
    evolution = fields.Selection([('n','Status Quo'),
                                  ('i','Improving'),
                                  ('w','Worsening')],
                                 string="Evolution")
    round_summary = fields.Text(string="Round Summary")
    gcs = fields.Many2one("medical.icu.glasgow",string="GOS")
    right_pupil = fields.Integer(string="R")
    pupillary_reactivity = fields.Selection([('brisk','Brisk'),
                                             ('sluggish','Sluggish'),
                                             ('nonreactive','Nonreactive')],
                                            string="Pupillary_Reactivity")
    pupil_dilation = fields.Selection([('normal','Normanl'),
                                       ('miosis','Miosis'),
                                       ('mydriasis','Mydriasis')],
                                      string="Pupil Dilation")
    left_pupil = fields.Integer(string="l")
    anisocoria = fields.Boolean(string="Anisocoria")
    pupil_consensual_resp  = fields.Boolean(string=" Consensual Response ")
    oxygen_mask = fields.Boolean(string='Oxygen Mask')
    respiration_type = fields.Selection([('regular','Regular'),
                                         ('deep','Deep'),
                                         ('shallow','Shallow'),
                                         ('labored','Labored'),
                                         ('intercostal','Intercostal')],
                                        string="Respiration")
    peep = fields.Boolean(string='Peep')
    sce = fields.Boolean(string='SCE')
    lips_lesion = fields.Boolean(string="Lips Lesion")
    fio2  = fields.Integer(string="FiO2")
    trachea_alignment  = fields.Selection([('midline','Midline'),
                                           ('right','Deviated Right'),
                                           ('left','Deviated Left')],
                                          string=' Tracheal alignment ')
    oral_mucosa_lesion = fields.Boolean(string=' Oral mucosa lesion ')
    chest_expansion = fields.Selection([('symmentric','Symmentrical'),
                                        ('asymmentric','Asynmmentrical')],
                                       string="Expansion")
    paradoxical_expansion = fields.Boolean(string="Paradoxical")
    tracheal_tug = fields.Boolean(string='Tracheal Tug')
    xray = fields.Binary(string="Xray")
    chest_drainages = fields.One2many('medical.icu.chest_drainage','medical_patient_rounding_chest_drainage_id',string="Chest Drainages")
    ecg = fields.Many2one('medical.icu.ecg',string="ECG")
    venous_access = fields.Selection([('none','None'),
                                      ('central','Central Catheter'),
                                      ('peripheral','Peripheral')],
                                     string="Venous Access")
    swan_ganz = fields.Boolean(string='Swan Ganz')
    arterial_access = fields.Boolean(string='Arterial Access')
    dialysis = fields.Boolean(string="Dialysis")
    edema = fields.Selection([('none','None'),
                              ('peripheral','Peripheral'),
                              ('anasarca','Anasarca')],
                             string='Edema')
    bacteremia = fields.Boolean(string="Becteremia")
    ssi = fields.Boolean(string='Surgery Site Infection')
    wound_dehiscence = fields.Boolean(string='Wound Dehiscence')
    cellulitis = fields.Boolean(string="Cellulitis")
    necrotizing_fasciitis = fields.Boolean(string=' Necrotizing fasciitis ')
    vomiting = fields.Selection([('none','None'),
                                 ('vomiting','Vomiting'),
                                 ('hematemesis','Hematemesis ')],
                                string="Vomiting")
    bowel_sounds = fields.Selection([('normal','Normal'),
                                     ('increased','Increased'),
                                     ('decreased','Decreased'),
                                     ('absent','Absent')],
                                    string="Bowel Sounds")
    stools = fields.Selection([('normal','Normal'),
                               ('constipation','Constipation'),
                               ('diarrhea','Diarrhea'),
                               ('melena','Melena')],
                              string="Stools")
    peritonitis = fields.Boolean(string="Peritonitis")
    procedures = fields.One2many('medical.rounding_procedure','medical_patient_rounding_procedure_id',string="Procedures")
    hospitalization_location = fields.Many2one('stock.location',string='Hospitalization Location')
    medicaments = fields.One2many('medical.patient.rounding.medicament','medical_patient_rounding_medicament_id',string="Medicaments")
    medical_supplies = fields.One2many('medical.patient.rounding.medical_supply','medical_patient_rounding_medical_supply_id',string='Medical Supplier')
    vaccines = fields.One2many('medical.patient.rounding.vaccine','medical_patient_rounding_vaccine_id',string='Vaccines')
    moves = fields.One2many('stock.move','medical_patient_rounding_move_id',string="Moves")
    state = fields.Selection([('draft','Draft'),
                              ('done','Done')],
                             string="Status")

class medical_icu_chest_drainage(models.Model):
    _name = 'medical.icu.chest_drainage'
    
    location = fields.Selection([('rl','Right Pleura'),
                                 ('ll','Left Pleura'),
                                 ('mediastinum','Mediastinum')],
                                string='Location')
    suction = fields.Boolean(string="Suction")
    suction_pressure = fields.Integer(string="cm H2O")
    fluid_volumme = fields.Integer(string="Volume")
    fluid_aspect = fields.Selection([('serous','Serous'),
                                     ('bloody','Bloody'),
                                     ('chylous','Chylous'),
                                     ('purulent','Purulent')],
                                    string="Aspect")
    oscillation = fields.Boolean(string='Oscillation')
    air_leak = fields.Boolean(string='Air Leak')
    remarks = fields.Char(string="Remarks")
    medical_patient_rounding_chest_drainage_id = fields.Many2one('medical.patient.rounding',string="Chest Drainage")
    
class medical_patient_rounding_medicament(models.Model):
    _name = 'medical.patient.rounding.medicament'
    
    medicament = fields.Many2one('medical.medicament',string='Medicament',required=True)
    quantity = fields.Integer(string="Quantity")
    lot = fields.Many2one('stock.production.lot',string='Lot',required=True)
    short_comment = fields.Char(string='Comment')
    product = fields.Many2one('product.product',string='Product')
    medical_patient_rounding_medicament_id = fields.Many2one('medical.patient.rounding',string="Medicaments") 
    
class medical_patient_rounding_medical_supply(models.Model):
    _name = 'medical.patient.rounding.medical_supply'
    
    product_id = fields.Many2one('product.product',string="Medical Supply",required=True)
    short_comment = fields.Char(string='Comment')
    quantity = fields.Integer(string="Quantity")
    lot = fields.Many2one('stock.production.lot',string='Lot',required=True)
    medical_patient_rounding_medical_supply_id = fields.Many2one('medical.patient.rounding',string=" Medical Supplies ")
    
class medical_patient_rounding_vaccine(models.Model):
    _name = 'medical.patient.rounding.vaccine'
    
    vaccines = fields.Many2one('product.product',string="Vaccines",required=True)
    quantity = fields.Integer(string="Quantity")
    lot = fields.Many2one('stock.production.lot',string='Lot',required=True)
    dose = fields.Integer(string="Dose")
    next_dose_date = fields.Datetime(string="Next Dose")
    short_comment = fields.Char(string='Comment')
    medical_patient_rounding_vaccine_id = fields.Many2one('medical.patient.rounding',string="Vaccines")
  
class medical_rounding_procedure(models.Model):
    _name = 'medical.rounding_procedure'

    procedure = fields.Many2one('medical.procedure',string="Code",required=True)   
    notes = fields.Text(string="Notes") 
    medical_patient_rounding_procedure_id = fields.Many2one('medical.patient.rounding',string="Vaccines")
    
class medical_procedure(models.Model):
    _name = 'medical.procedure'

    name = fields.Char(string='Code',required=True)
    description = fields.Text(string='Long Text')
       
class stock_move(models.Model):
    _inherit = 'stock.move'  
    
    medical_patient_rounding_move_id = fields.Many2one('medical.patient.rounding',string="Medical Patient Rounding")
    
class medical_patient_ambulatory_care(models.Model):
    _name = 'medical.patient.ambulatory_care'

    name = fields.Char(string='Id',readonly=True,size=256)
    ordering_professional = fields.Many2one('medical.physician',string='Ordering Physician')
    base_condition = fields.Many2one('medical.pathology',string='Base Condition')
    session_number = fields.Integer(string = 'Session #',required=True)
    health_professional = fields.Many2one('medical.physician',string='Health Professional',readonly=True)
    patient = fields.Many2one('medical.patient',string='Patient',required=True)
    evaluation = fields.Many2one('medical.patient.evaluation',string='Related Evaluation')
    session_start = fields.Datetime(string='Start',required=True)
    state = fields.Selection([('done','Done'),
                              ('draft','Draft')],
                             string='Status')
    procedures = fields.One2many('medical.ambulatory_care_procedure','medical_patient_ambulatory_care_procedure_id')
    session_notes = fields.Text(string='Session',required=True,default='Stable')
    warning = fields.Boolean(string='Warning')
    session_end = fields.Datetime(string="End",required=True)
    next_session = fields.Datetime(string='Next Session')
    temperature =fields.Float(string='Temperature')
    systolic = fields.Integer(string="Systolic Pressure")
    diastolic = fields.Integer(string='Diastolic Pressure')
    bpm = fields.Integer(string='Heart Rate')
    respiratory_rate = fields.Integer(string="Respiratory Rate")
    osat = fields.Integer(string="Oxygen Saturation")
    glycemia = fields.Integer(string="Glycemia")
    evolution = fields.Selection([('initial','Initial'),
                                  ('n','Status Quo'),
                                  ('i','Improving'),
                                  ('w','Worsening')],
                                 string="Evolution")
    care_location = fields.Many2one('stock.location',string='Care Location')
    medicaments = fields.One2many('medical.patient.ambulatory_care.medicament','medical_patient_rounding_ambulatory_care_medicament_id',string='Medicaments')
    medical_supplies = fields.One2many('medical.patient.ambulatory_care.medical_supply','medical_patient_rounding_ambulatory_care_supply_id',string='Medical Supplier')
    vaccines = fields.One2many('medical.patient.ambulatory_care.vaccine','medical_patient_ambulatory_care_vaccine_id',string='Vaccines')
    moves = fields.One2many('stock.move','medical_patient_rounding_move_id',string="Moves")
    
class medical_ambulatory_care_procedure(models.Model):
    _name = 'medical.ambulatory_care_procedure'

    procedure_id = fields.Many2one('medical.procedure',string="Code",required=True)   
    comments = fields.Char(string="Comments") 
    medical_patient_ambulatory_care_procedure_id = fields.Many2one('medical.patient.ambulatory_care',string="Procedure")
    
class medical_procedure(models.Model):
    _name = 'medical.procedure'

    name = fields.Char(string='Code',required=True)
    description = fields.Text(string='Long Text')
    
class medical_patient_ambulatory_care_medicament(models.Model):
    _name = 'medical.patient.ambulatory_care.medicament'
    
    medicament = fields.Many2one('medical.medicament',string='Medicament',required=True)
    quantity = fields.Integer(string="Quantity")
    lot = fields.Many2one('stock.production.lot',string='Lot',required=True)
    short_comment = fields.Char(string='Comment')
    product = fields.Many2one('product.product',string='Product')
    medical_patient_rounding_ambulatory_care_medicament_id = fields.Many2one('medical.patient.ambulatory_care',string="Medicaments") 
    
class medical_patient_ambulatory_care_medical_supply(models.Model):
    _name = 'medical.patient.ambulatory_care.medical_supply'
    
    product_id = fields.Many2one('product.product',string="Medical Supply",required=True)
    short_comment = fields.Char(string='Comment')
    quantity = fields.Integer(string="Quantity")
    lot = fields.Many2one('stock.production.lot',string='Lot',required=True)
    medical_patient_rounding_ambulatory_care_supply_id = fields.Many2one('medical.patient.ambulatory_care',string=" Medical Supplies ")
    
class medical_patient_ambulatory_care_vaccine(models.Model):
    _name = 'medical.patient.ambulatory_care.vaccine'
    
    vaccines = fields.Many2one('product.product',string="Vaccines",required=True)
    quantity = fields.Integer(string="Quantity")
    lot = fields.Many2one('stock.production.lot',string='Lot',required=True)
    dose = fields.Integer(string="Dose")
    next_dose_date = fields.Datetime(string="Next Dose")
    short_comment = fields.Char(string='Comment')
    medical_patient_ambulatory_care_vaccine_id = fields.Many2one('medical.patient.ambulatory_care',string="Vaccines")
  
class stock_move(models.Model):
    _inherit = 'stock.move'  
    
    medical_patient_rounding_move_id = fields.Many2one('medical.patient.ambulatory_care',string="Medical Patient Rounding")
    