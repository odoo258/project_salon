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

from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError
from datetime import date, datetime, timedelta
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
from logging import getLogger

_logger = getLogger(__name__)


class medical_bed_transfer_wizard(models.TransientModel):
    _name = "medical.bed.transfer.wizard"
    _recname = 'newbed'

    newbed = fields.Many2one('medical.hospital.bed', string="New Bed", required=True)
    reason = fields.Char('Reason', required=True)

    def bed_transfer(self, cr, uid, id, context=None):
        record = self.browse(cr, uid, id, context=context)
        medic_imp_obj = self.pool.get('medical.inpatient.registration')
        medic_imp_rec = medic_imp_obj.browse(cr, uid, context.get('active_id'), context=None)
        if medic_imp_rec.state == 'hospitalized':
            if record.newbed.state == 'free':
                record.newbed.state = 'occuiped'
                medic_imp_rec.bed = record.newbed.id
                medic_imp_obj.write(cr, uid, context.get('active_id'),
                                    {'bed': record.newbed.id, 'bed_transfers': [(0, 0, {'date': date.today(),
                                                                                        'bed_to': record.newbed.id,
                                                                                        'bed_from': medic_imp_rec.bed.id,
                                                                                        'inpatient_id': medic_imp_rec.patient.id,
                                                                                        'reason': record.reason, })]},
                                    context=context)
        res = self.pool.get('bed.transfer').create(cr, uid, {'date': date.today(),
                                                             'bed_to': record.newbed.id,
                                                             'bed_from': medic_imp_rec.bed.id,
                                                             'inpatient_id': medic_imp_rec.patient.id,
                                                             'reason': record.reason, })


class MedicalInpatientRegistration(models.Model):
    _name = 'medical.inpatient.registration'
    _inherit = 'mail.thread'

    name = fields.Char(string="Registration Code", copy=False, readonly=True, index=True)
    owner_id = fields.Many2one(
        'res.partner', string="Owner", required=True, domain=[('is_owner', '=', True)]
    )
    patient = fields.Many2one(
        'medical.patient', string="Pet", required=True, domain="[('owner_id', '=', owner_id)]"
    )
    bed = fields.Many2one(
        'medical.hospital.bed',
        string="Hospital Bed"
    )
    hospitalization_date = fields.Datetime(
        string="Hospitalization date", required=True
    )
    discharge_date = fields.Datetime(
        string="Expected Discharge date"
    )
    start_admission_date = fields.Datetime(
        string="Start Admission Date", track_visibility='onchange'
    )

    attending_physician = fields.Many2one('medical.physician', string="Attending Physician")
    operating_physician = fields.Many2one('medical.physician', string="Operating Physician")
    admission_type = fields.Selection(
        string="Admission Type", selection=[
            ('routine', 'Routine'),
            ('maternity', 'Maternity'),
            ('elective', 'Elective'),
            ('urgent', 'Urgent'),
            ('emergency', 'Emergency  ')
        ])
    info = fields.Text(string="Extra Info")
    bed_transfers = fields.One2many('bed.transfer', 'inpatient_id', string='Transfer Bed', readonly=True)
    diet_belief = fields.Many2one('medical.diet.belief', string='Belief')
    therapeutic_diets = fields.One2many('medical.inpatient.diet', 'inpatient_id', string='Therapeutic_diets')
    diet_vegetarian = fields.Selection([('none', 'None'), ('vegetarian', 'Vegetarian'), ('lacto', 'Lacto Vegetarian'),
                                        ('lactoovo', 'Lacto-Ovo-Vegetarian'), ('pescetarian', 'Pescetarian'),
                                        ('vegan', 'Vegan')], string="Vegetarian")
    nutrition_notes = fields.Text(string="Nutrition notes / Directions")
    state = fields.Selection(string="State", default="open", selection=[
        ('open', _('Open')),
        ('schedule', _('Schedule')),
        ('pending_payment', _('Pending Payment')),
        ('done', _('Done'))
    ], track_visibility='onchange')
    nursing_plan = fields.Text(string="Nursing Plan")
    discharge_plan = fields.Text(string="Discharge Plan")
    icu = fields.Boolean(string="ICU")
    medicatin_ids = fields.One2many('medical.inpatient.medication', 'medical_inpatient_medication_id',
                                    string='Medication')
    icu_admissions = fields.One2many('medical.inpatient.icu', 'name', string='ICU Ids', readonly=True)
    evaluation_ids = fields.One2many(
        'medical.inpatient.evaluation', 'medical_inpatient_registration_id',
        string="Evaluations"
    )
    inpatient_medication_ids = fields.One2many(
        'medical.inpatient.medication1', 'medical_inpatient_registration_id',
        string=_("Medications")
    )
    inpatient_vaccination_ids = fields.One2many(
        'medical.vaccination', 'medical_inpatient_registration_id',
        string=_("Vaccination")
    )
    surgery_ids = fields.One2many(
        'medical.surgery', 'medical_inpatient_registration_id',
        string=_("Surgery")
    )
    lab_test_ids = fields.One2many(
        'medical.patient.lab.test', 'medical_inpatient_registration_id',
        string=_("Lab Test")
    )
    map_ids = fields.One2many(
        'medical.map', 'admission_id',
        string=_("Map")
    )
    admission_reactivate_ids = fields.One2many(
        'admission.reactivate.log', 'admission_id',
        string="Reactivate Log"
    )
    amount_gross = fields.Float(
        string="Total Gross (=)", compute='_compute_amount'
    )
    amount_approved = fields.Float(
        string="Total Approved (+)", compute='_compute_amount'
    )
    amount_open = fields.Float(
        string="Total Open (-)", compute='_compute_amount'
    )
    amount_draft = fields.Float(
        string="Total Draft (-)", compute='_compute_amount'
    )
    amount_disapproved = fields.Float(
        string="Total Dissaproved (-)", compute='_compute_amount'
    )
    amount_total = fields.Float(
        string="Amount Total", compute='_compute_amount'
    )
    sale_order_ids = fields.One2many(
        'sale.order', 'admission_id',
        string="Sale Order"
    )
    log_ids = fields.One2many(
        'medical.map.log', 'admission_id', string="Medical Records"
    )
    step_ids = fields.One2many(
        'medical.map.step', 'admission_id', string="Medical Steps"
    )

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('medical.inpatient.registration')
        result = super(MedicalInpatientRegistration, self).create(vals)
        return result

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        xfilter = self._context.get('filter')
        # BUSCAR ATENDIMENTOS EM ESPERA
        if xfilter == 'wait':
            time_alert = int(self.env['ir.config_parameter'].get_param('time_alert', default=0))
            now = fields.Datetime.context_timestamp(self, datetime.now()) + timedelta(minutes=int(time_alert))
            xargs = [
                ('state', '=', 'schedule'),
                ('hospitalization_date', '<=', fields.Datetime.to_string(now))
            ]
            ma = self.env.get('medical.inpatient.registration').with_context(filter=None)
            return ma.search(xargs)

        return super(MedicalInpatientRegistration, self).search(
            args, offset=offset, limit=limit, order=order, count=count
        )


    @api.multi
    def check_admission(self):
        """verifica se tem paciente aguardando atendimento depois de um tempo de espera estimado"""
        time_alert = int(self.env['ir.config_parameter'].get_param('time_alert', default=0))
        users = self.env['ir.config_parameter'].get_param('users', default='[]')
        _logger.debug("Time Alert: {} - Users: {}".format(time_alert, users))
        if time_alert and users:
            xml_id = self.env['ir.actions.act_window'].for_xml_id('hospital_management',
                                                                  'medical_action_form_inpatient_wait')
            now = fields.Datetime.context_timestamp(self, datetime.now()) + timedelta(minutes=int(time_alert))
            args = [
                ('state', '=', 'schedule'),
                ('hospitalization_date', '<=', fields.Datetime.to_string(now))
            ]
            admissions_count = self.env['medical.inpatient.registration'].search_count(args)
            _logger.debug("Admission Count: {%s} - Args: {%s}" % (admissions_count, args))
            if admissions_count:
                for user in self.env['res.users'].browse(eval(users)):
                    if user.company_id.is_hospital:
                        _logger.debug(u"Notify user: {%s}" % (user.name))
                        user.notify_warning(
                            message=_(
                                "%02d patient(s) waiting for care <a style='color: black' href='/web#min=1&limit=80&"
                                "view_type=list&model=medical.inpatient.registration&action=%d' class='pull-right'>"
                                "GO <i class='fa fa-external-link'></i></a>" % (admissions_count, xml_id.get('id'))
                            ), sticky=True
                        )
                    else:
                        _logger.debug("User %s is not in a hospital company" % (user.name))

    @api.multi
    def button_dummy(self):
        return True

    @api.multi
    def view_log(self):
        tree_id = self.env.ref('hospital_management.medical_map_log_view_tree').id
        form_id = self.env.ref('hospital_management.medical_map_log_view_form').id
        search_id = self.env.ref('hospital_management.medical_map_log_search').id

        ret = {
            'type': 'ir.actions.act_window',
            'name': _('Log'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'medical.map.log',
            'domain': [('admission_id', '=', self.id)],
            'views': [(tree_id, 'tree'), (form_id, 'form')],
            'search_view_id': search_id,
            'context': {
                'search_default_date': 1,
                'search_default_map': 1
            }
        }
        print(ret)
        return ret

    @api.one
    def btn_start_admission(self):
        if not self.start_admission_date:
            self.start_admission_date = datetime.now()
        self.state = 'schedule'

    @api.one
    def btn_done_admission(self):
        for line in self.map_ids:
            #if not line.state == 'closed':
            if not line.sale_approved == 'approved':
                raise UserError("Todas as OS devem estar pagas para finalizar a ficha")
        self.state = 'done'

    @api.one
    def btn_reactivate_admission(self):
        self.state = 'open'

    @api.one
    def action_done(self):
        for line in self.map_ids:
            #if not line.state == 'closed':
            if not line.sale_approved == 'approved':
                raise UserError("Todas as OS devem estar pagas para finalizar a ficha")
        self.write({'state': 'done'})

    @api.depends('map_ids')
    def _compute_amount(self):
        maps = self.map_ids
        for omap in maps:
            price = omap.service_id.list_price
            state = omap.state
            self.amount_gross += price
            #if state in ['approved', 'closed']:
            if state in ['approved', 'done']:
                self.amount_approved += price
            #elif state == 'open':
            elif state == 'schedule':
                self.amount_open += price
            elif state == 'draft':
                self.amount_draft += price
            elif state == 'disapproved':
                self.amount_disapproved += price
        self.amount_total = self.amount_approved

    @api.multi
    def open_wizard(self):
        order_ids = []
        for map in self.map_ids:
            order_id = map.sale_order_line_id.order_id.id
            state = map.sale_order_line_id.order_id.state
            if order_id and state == 'draft':
                order_ids.append(order_id)
        self.ensure_one()
        return {
            'name': _('Make Quotation'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'map.quotation.wizard',
            'view_id': self.env.ref('hospital_management.map_quotation_form_view_wizard').id,
            'target': 'new',
            'context': {
                'admission_ids': self.ids, 'order_ids': order_ids, 'invisible': False if order_ids else True
            },
        }

    @api.multi
    def create_invoice(self):
        raise UserError("Não Implementado")

    @api.multi
    def make_quotation(self):
        raise UserError("Não Implementado")

    @api.one
    def btn_join_quotation(self):
        orders = self.env['sale.order'].search([
            ('admission_id', '=', self.id), ('state', '=', 'sale')
        ])
        if len(orders) <= 1:
            raise UserError(_('There are no sales orders to merge'))
        else:
            itens = False
            new_order = self.env['sale.order'].create({'partner_id': self.owner_id.id})
            new_order.admission_id = self.id
            for order in orders:
                order.action_cancel()
                order.admission_id = False
                for item in order.order_line:
                    item.order_id = new_order.id
                order.unlink()


class AdmissionReactivateLog(models.Model):
    _name = 'admission.reactivate.log'
    REASONS = [
        ('op1', _('Option 01')),
        ('op2', _('Option 02')),
        ('op3', _('Option 03')),
        ('op4', _('Option 04')),
        ('other', _('Other'))
    ]
    name = fields.Selection(
        string="Reason for Reactivation", selection=REASONS, required=True
    )
    observation = fields.Text(
        string="Observation", required=True
    )
    admission_id = fields.Many2one(
        'medical.inpatient.registration', string="Admission"
    )


class MedicalInpatientServices(models.Model):
    _name = 'medical.inpatient.services'

    name = fields.Char(
        string="OS #"
    )
    type = fields.Selection(
        string="Type", required=True, selection=[
            ('surgery', _('Surgery')),
            ('lab_test', _('Lab Test'))
        ]
    )
    state = fields.Selection(
        string="State", default='draft', selection=[
            ('draft', _('Draft')),
            ('approved', _('Approved')),
            ('disapproved', _('Disapproved')),
            ('open', _('Open')),
            ('closed', _('Closed'))
        ]
    )
    doctor_id = fields.Many2one(
        'medical.physician', string="Doctor"
    )
    service_id = fields.Many2one(
        'product.product', string='Service',
    )
    is_approved = fields.Boolean(
        string="Approved"
    )
    expected_date = fields.Date(
        string="Expected Date", required=True
    )
    additional_information = fields.Text(
        string="Additional Information"
    )
    admission_id = fields.Many2one('medical.inpatient.registration', string='Admission')

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('medical.inpatient.service.seq')
        result = super(MedicalInpatientServices, self).create(vals)
        return result


class bed_transfer(models.Model):
    _name = 'bed.transfer'

    date = fields.Datetime(string='Date')
    bed_from = fields.Char(string='From')
    bed_to = fields.Char(string='To')
    reason = fields.Text(string='Reason')
    inpatient_id = fields.Many2one('medical.inpatient.registration', string='Inpatient Id')


class medical_diet_belief(models.Model):
    _name = 'medical.diet.belief'

    code = fields.Char(string='Code', required=True)
    description = fields.Text(string='Description', required=True)
    name = fields.Char(string='Belief')


class medical_inpatient_diet(models.Model):
    _name = 'medical.inpatient.diet'

    diet = fields.Many2one('medical.diet.therapeutic', string='Diet', required=True)
    remarks = fields.Text(string=' Remarks / Directions ')
    inpatient_id = fields.Many2one('medical.inpatient.registration', string='Inpatient Id')


class medical_diet_therapeutic(models.Model):
    _name = 'medical.diet.therapeutic'

    name = fields.Char(string='Diet Type', required=True)
    code = fields.Char(string='Code', required=True)
    description = fields.Text(string='Description', required=True)


class medical_inpatient_icu(models.Model):
    _name = 'medical.inpatient.icu'

    name = fields.Many2one('medical.inpatient.registration', string="Registration Code", required=True)
    admitted = fields.Boolean(string="Admitted", required=True, default=True)
    icu_admission_date = fields.Datetime(string="ICU Admission", required=True)
    icu_stay = fields.Char(string="Duration", required=True, size=128)
    discharged_from_icu = fields.Boolean(string="Discharged")
    icu_discharge_date = fields.Datetime(string='Discharge')
    mv_history = fields.One2many('medical.icu.ventilation', 'mi_icu_id', string='MV History')

    @api.multi
    def onchange_patient(self, name):
        inpatient_brw = self.env['medical.inpatient.registration'].browse(name)
        inpatient_name = inpatient_brw.name

        inpatient_icu_obj = self.env['medical.inpatient.icu']
        inpatient_icu_ids = inpatient_icu_obj.search([('name.name', '=', inpatient_name)])
        if len(inpatient_icu_ids) > 1:
            raise UserError(_('Our records indicate that the patient is already admitted at ICU. '))

    @api.multi
    def onchange_with_descharge(self, admitted, discharged_from_icu):
        res = {}
        if discharged_from_icu == True:
            res.update({'admitted': False})
        else:
            res.update({'admitted': True})
        return {'value': res}

    @api.multi
    def onchange_with_admitted(self, admitted, discharged_from_icu):
        res = {}
        if admitted == True:
            res.update({'discharged_from_icu': False})
        else:
            res.update({'discharged_from_icu': True})
        return {'value': res}


class medical_icu_ventilation(models.Model):
    _name = 'medical.icu.ventilation'

    current_mv = fields.Boolean(string="Current", required=True, default=True)
    mv_start = fields.Datetime(string="From", required=True)
    mv_end = fields.Datetime(string="To", required=True)
    mv_period = fields.Char(string="Duration", size=128, required=True)
    ventilation = fields.Selection(
        [('none', 'None - Maintains Own'), ('nppv', 'Non-Invasive Psitive Pressure'), ('ett', 'ETT'),
         ('tracheostomy', 'Tracheostomy')], string="Type")
    remarks = fields.Char(string="Remarks")
    mi_icu_id = fields.Many2one('medical.inpatient.icu', string="Inpatient ICU")


class medical_icu_glasgow(models.Model):
    _name = 'medical.icu.glasgow'

    name = fields.Many2one('medical.inpatient.registration', string="Registration Code", required=True)
    evaluation_date = fields.Datetime(string="Date", required=True)
    glasgow_eyes = fields.Selection([('1', '1 : Does not Open Eyes'),
                                     ('2', '2 : Opens eyes in response to painful Stimuli'),
                                     ('3', '3 : Open eyes to response to voice'),
                                     ('4', '4 : Open eyes spontaneously')],
                                    string="Eyes")
    glasgow_verbal = fields.Selection([('1', '1 : Makes no sounds'),
                                       ('2', '2 : Incomprehensible Sounds'),
                                       ('3', '3 : Utters inapporopriate words'),
                                       ('4', '4 : Confused disoriented'),
                                       ('5', '5 : Oriented converses normally')],
                                      string="Verbal")
    glasgow_motor = fields.Selection([('1', '1 : Makes no movement'),
                                      ('2', '2 : Extension to painful stimuli -decerabrate response'),
                                      ('3', '3 : Abnormal flexion to painful stimuli (decorticate response)'),
                                      ('4', '4 : Flexion/Withdrawal to painful stimuli'),
                                      ('5', '5 : Localizes painful stimuli'),
                                      ('6', '6 : Obeys commands')],
                                     string="Motor")
    glasgow = fields.Integer(string="Glasgow", compute='get_glas_score')

    @api.one
    @api.depends('glasgow_motor', 'glasgow_verbal', 'glasgow_eyes')
    def get_glas_score(self):
        """ Calculates Sub total"""
        count = int(self.glasgow_eyes) + int(self.glasgow_motor) + int(self.glasgow_verbal)
        self.glasgow = count


class medical_icu_ecg(models.Model):
    _name = 'medical.icu.ecg'

    ecg_date = fields.Datetime(string="Date", requied=True)
    name = fields.Many2one('medical.inpatient.registration', string="Registration Code", required=True)
    lead = fields.Selection(
        [('i', '|'), ('ii', '||'), ('iii', '|||'), ('avf', 'aVF'), ('avr', 'aVR'), ('avl', 'aVL'), ('v1', 'V1'),
         ('v2', 'V2'), ('v3', 'V3'), ('v4', 'V4'), ('v5', 'V5'), ('v6', 'V6')])
    axis = fields.Selection([('normal', 'Normal'), ('left', 'Left Deviation'), ('right', 'Right Deviation'),
                             ('extreme_right', 'Extreme Right Deviation')], string="Axis", required=True)
    rate = fields.Integer(string="Rate", required="True")
    pacemaker = fields.Selection([('sa', 'sinus Node'), ('av', 'Atrioventricular'), ('pk', 'purkinje')],
                                 string="Pacemaker", required=True)
    rhythm = fields.Selection([('regular', 'Regular'), ('irregular', 'Irregular')], string="Rhythm", required=True)
    pr = fields.Integer(string="PR", required=True)
    qrs = fields.Integer(string="QRS", required=True)
    qt = fields.Integer(string="QT", required=True)
    st_segment = fields.Selection([('normal', 'Normal'), ('depressed', 'Depressed'), ('elevated', 'Elevated')],
                                  string="ST Segment", required=True)
    twave_inversion = fields.Boolean(string="T Wave Inversion")
    interpretation = fields.Char(string="Interpretation", required=True, size=256)


class medical_icu_apache2(models.Model):
    _name = 'medical.icu.apache2'

    name = fields.Many2one('medical.inpatient.registration', string="Registration Code", required=True)
    score_date = fields.Datetime(string="Date", required=True)
    age = fields.Integer(string="Age")
    temperature = fields.Float(string="Temperature")
    heart_rate = fields.Float(string="Heart Rate")
    fio2 = fields.Float(string="Fio2")
    paco2 = fields.Float(string="PaCO2")
    ph = fields.Float(string="pH")
    serum_potassium = fields.Float(string="Potassium")
    hematocrit = fields.Float(string="Hematcocrit")
    arf = fields.Boolean(string="ARF")
    mean_ap = fields.Integer(string="MAP")
    respiratory_rate = fields.Integer(string='Respiratory Rate')
    pao2 = fields.Integer(string="PaO2")
    aado2 = fields.Integer(string="A-a DO2")
    serum_sodium = fields.Integer(string="Sodium")
    serum_creatinine = fields.Float(string="Creatinine")
    wbc = fields.Float(string="WBC")
    chronic_condition = fields.Boolean(string="Chronic Condition")
    apache_score = fields.Integer(string="Score")
    hospital_admission_type = fields.Selection(
        [('me', 'Medical or emergency postoperative'), ('el', 'elective postoperative')],
        string="Hospital Admission Type")


class medical_inpatient_medication(models.Model):
    _name = 'medical.inpatient.medication'

    medicament = fields.Many2one('medical.medicament', string='Medicament', required=True)
    is_active = fields.Boolean(string='Active')
    start_treatment = fields.Datetime(string='Start Of Treatment', required=True)
    course_completed = fields.Boolean(string="Course Completed")
    doctor = fields.Many2one('medical.physician', string='Physician')
    indication = fields.Many2one('medical.pathology', string='Indication')
    end_treatment = fields.Datetime(string='End Of Treatment', required=True)
    discontinued = fields.Boolean(string='Discontinued')
    form = fields.Many2one('medical.drug.form', string='Form')
    route = fields.Many2one('medical.drug.route', string=" Administration Route ")
    dose = fields.Float(string='Dose')
    qty = fields.Integer(string='X')
    dose_unit = fields.Many2one('medical.dose.unit', string='Dose Unit')
    duration = fields.Integer(string="Treatment Duration")
    duration_period = fields.Selection([('minutes', 'Minutes'),
                                        ('hours', 'hours'),
                                        ('days', 'Days'),
                                        ('months', 'Months'),
                                        ('years', 'Years'),
                                        ('indefine', 'Indefine')], string='Treatment Period')
    common_dosage = fields.Many2one('medical.medication.dosage', string='Frequency')
    admin_times = fields.Char(string='Admin Hours')
    frequency = fields.Integer(string='Frequency')
    frequency_unit = fields.Selection([('seconds', 'Seconds'),
                                       ('minutes', 'Minutes'),
                                       ('hours', 'hours'),
                                       ('days', 'Days'),
                                       ('weeks', 'Weeks'),
                                       ('wr', 'When Required')], string='Unit')
    adverse_reaction = fields.Text(string='Notes')
    medical_inpatient_medication_id = fields.Many2one('medical.inpatient.registration', string='Medication')
    admin_times = fields.One2many('medical.inpatient.medication.admin.time', 'medical_inpatient_admin_time_id',
                                  string='Admin')
    log_history = fields.One2many('medical.inpatient.medication.log', 'medication_log_id', string='Log History')


class medical_inpatient_medication_log(models.Model):
    _name = 'medical.inpatient.medication.log'

    admin_time = fields.Datetime(string='Date', readonly=True)
    dose = fields.Float(string='Dose')
    remarks = fields.Text(string='Remarks')
    health_professional = fields.Many2one('medical.physician', string='Health Professional', readonly=True)
    dose_unit = fields.Many2one('medical.dose.unit', string='Dose Unt')
    medication_log_id = fields.Many2one('medical.inpatient.medicament', string='Log History')


class medical_inpatient_medication_admin_time(models.Model):
    _name = 'medical.inpatient.medication.admin.time'

    admin_time = fields.Datetime(string='Date')
    dose = fields.Float(string='Dose')
    remarks = fields.Text(string='Remarks')
    health_professional = fields.Many2one('medical.physician', string='Health Professional')
    dose_unit = fields.Many2one('medical.dose.unit', string='Dose Unt')
    medical_inpatient_admin_time_id = fields.Many2one('medical.inpatient.medicament', string='Admin Time')

    # vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:s
