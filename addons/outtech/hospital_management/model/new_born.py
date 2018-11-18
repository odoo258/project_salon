# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 BrowseInfo (<http://Browseinfo.in>).
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
##############################################################################
from openerp import api, fields, models, _
from datetime import date

class medical_neomatal_apgar(models.Model):
     
    _name  =  'medical.neomatal.apgar'
    _rec_name = 'new_born_id'
    
    new_born_id = fields.Many2one('medical.newborn', 'Name')
    apgar_activity = fields.Selection([('0', 'None'),('1','Some Flexion'),('2','Fixed Arm and Legs')], 'Activity')
    apgar_appearance = fields.Selection([('0', 'Central cyanosis'),('1', 'Acrosynosis'), ('2', 'No Cynosis')], 'Appearance')
    apgar_grimace = fields.Selection([('0', 'No response to simulation'), ('1','Grimance when simulated'),('2','Cry Or pull away when simulated')], 'Grimace')
    apgar_minute  = fields.Integer('Minute', required = True)
    apgar_respiration = fields.Selection([('0', 'Absent'),('1', 'Weak / Irregular'),('2', 'Strong')], 'Respiration')
    apgar_pulse = fields.Selection([('0', 'None'), ('1', '< 100'), ('2','> 100')], 'Pulse')
    apgar_scores = fields.Integer('Apgar Score')
    
    @api.onchange('apgar_activity' , 'apgar_appearance', 'apgar_grimace', 'apgar_minute', 'apgar_respiration', 'apgar_pulse',)
    def on_change_selection(self):
        self.apgar_scores = int(self.apgar_activity)+ int(self.apgar_appearance)+ int(self.apgar_grimace)+ int(self.apgar_minute)+ int(self.apgar_respiration)+int(self.apgar_pulse)
         
    
     
    

class medical_newborn(models.Model):

    _name = 'medical.newborn'
    
    name = fields.Char('Name', readonly = True)
    mother_id = fields.Many2one('medical.patient','Mother', domain="[('sex', '=', 'f')]")
    birth_date  = fields.Date('Date of Birth' , required = True)
    length = fields.Integer('Length', )
    cephalic_perimeter = fields.Integer('Cephalic Perimeter')
    baby_name  = fields.Char('Baby\'s name')
    sex  = fields.Selection([('m','Male'), ('f','Female'),('a','Ambiguous Genitalia ')], required = True ) 
    dismissed  = fields.Datetime('Discharged')
    weight = fields.Integer('Weight')
    responsible_id = fields.Many2one('medical.physician','Doctor in charge')
    photo = fields.Binary('Picture')
    meconium = fields.Boolean('Meconium')
    neonatal_ambiguous_genitalia = fields.Boolean('Ambiguous Genitalia')
    neonatal_babinski_reflex = fields.Boolean('Babinski Reflex')
    neonatal_barlow = fields.Boolean('Positive Barlow')
    neonatal_blink_reflex = fields.Boolean('Blink Reflex')
    neonatal_erbs_palsy = fields.Boolean('Erbs Palsy')
    neonatal_grasp_reflex =fields.Boolean('Grasp Reflex')
    neonatal_hematoma = fields.Boolean('Hematomas')
    neonatal_hernia = fields.Boolean('Hernia')
    neonatal_moro_reflex = fields.Boolean('Moro Reflex')
    neonatal_ortolani = fields.Boolean('Positive Ortolani')
    neonatal_palmar_crease = fields.Boolean('Transversal Palmar Crease')
    neonatal_polydactyly = fields.Boolean('Polydactyly')
    neonatal_rooting_reflex = fields.Boolean('Rooting Reflex')
    neonatal_stepping_reflex = fields.Boolean('Stepping Reflex')
    neonatal_sucking_reflex = fields.Boolean('Sucking Reflex')
    neonatal_swimming_reflex = fields.Boolean('Swimming Reflex')
    neonatal_syndactyly = fields.Boolean('Syndactyly')
    neonatal_talipes_equinovarus = fields.Boolean('Talipes Equinovarus')
    neonatal_tonic_neck_reflex = fields.Boolean('Tonic Neck Reflex')
    died_at_delivery = fields.Boolean('Died at delivery room')
    died_being_transferred = fields.Boolean('Died at Transfered')
    died_at_the_hospital = fields.Boolean('Died at the hospital')
    
    reanimation_aspiration = fields.Boolean('Aspiration')
    reanimation_intubation = fields.Boolean('Intubation')
    reanimation_mask = fields.Boolean('Mask')
    reanimation_oxygen = fields.Boolean('Oxygen')
    reanimation_stimulation = fields.Boolean('Stimulation')
    test_audition = fields.Boolean('Audition')
    test_billirubin = fields.Boolean('Billirubin')
    test_chagas = fields.Boolean('Chagas')
    test_metabolic = fields.Boolean('Metabolic ("heel stick screening")')
    test_toxo = fields.Boolean('Toxoplasmosis')
    test_vdrl = fields.Boolean('VDRL')
    bd = fields.Boolean('Stillbirth')
    tod = fields.Datetime('Time of Death')
    notes = fields.Text('Notes')
    cod = fields.Many2one('medical.pathology','Cause Of Death')
    congenital_disease_ids = fields.One2many('medical.patient.disease', 'new_born_id')
    inpatient_medication_ids = fields.One2many(
        'medical.inpatient.medication1', 'new_born_id'
    )
    apgar_score_ids = fields.One2many('medical.neomatal.apgar', 'new_born_id')
    
    def create(self, cr, uid, val, context = None):
        val['name'] = self.pool.get('ir.sequence').next_by_code(cr, uid, 'new_born_seq')
        result = super(medical_newborn, self).create(cr, uid, val)
        return result

    @api.multi
    def print_card(self):
        return self.env['report'].get_action(self, 'hospital_management.report_newborn_card')
    
    
    
class medical_patient_diseases(models.Model):
    
    _name = 'medical.patient.diseases'
    
    new_born_id = fields.Many2one('medical.newborn')
    pathelogh_id = fields.Many2one('medical.pathology', 'Disease')
    status_of_the_disease = fields.Selection([('chronic','Chronic'),('status quo','Status Quo'),('healed','Healed'), ('improving','Improving'), ('worsening', 'Worsening') ], 'Status of the disease')
    is_active = fields.Boolean('Active Disease')
    diagnosed_date = fields.Date('Date of Diagnosis')
    age = fields.Date('Age when diagnosed')
    disease_severity = fields.Selection([('mild','Mild'), ('moderate','Moderate'), ('severe','Severe')], 'Severity')
    is_infectious = fields.Boolean('Infectious Disease', help = 'Check if the patient has an infectious / transmissible disease')
    short_comment = fields.Char('Remarks')
    healed_date = fields.Date('Healed')
    physician_id = fields.Many2one('medical.patient','Doctor')
    is_allergy = fields.Boolean('Allergic Disease')
    is_infectious = fields.Boolean('Infectious Disease')
    allergy_type  = fields.Selection([('drug_allergy', 'Drug Allergy'),('food_allergy', 'Food Allergy'),('misc', 'Misc')], 'Allergy_type')
    pregnancy_warning = fields.Boolean('Pregnancy warning')
    weeks_of_pregnancy = fields.Integer('Contracted in pregnancy week #')
    is_on_treatment = fields.Boolean('Currently on Treatment')
    treatment_description = fields.Char('Treatment Description')
    date_start_treatment = fields.Date('Start of treatment')
    date_stop_treatment = fields.Date('End of treatment')
    psc_code_id = fields.Many2one('psc.code', 'Code')
    
    
    
     
class psc_code(models.Model):
    
    _name  = 'psc.code'
    
    name = fields.Char('Code', required =True) 
    description = fields.Text('Long Text', required =True)
  
  

class medical_patient_medication(models.Model):
    
    _name = 'medical.patient.medication'
    _rec_name = 'medical_medicament_id'
    
    medical_medicament_id = fields.Many2one('medical.medicament', 'Medicament')
    new_born_id =  fields.Many2one('medical.newborn', 'New Born')
    is_active =  fields.Boolean('Active')
    start_treatment = fields.Datetime('Start of treatment')
    course_completed = fields.Boolean('Course Completed')
    physician_id = fields.Many2one('medical.patient','Physician')
      
  
    
    
class medicament_category(models.Model):
    
    
    _name = 'medicament.category'
    
    name = fields.Char('Name', required = True)
    parent_id = fields.Many2one('medicament.category', 'Parent')
    
      
            
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:    