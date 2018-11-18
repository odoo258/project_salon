# coding=utf-8
# Author: Christian Douglas <christian.douglas.alcantara@gmail.com>
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime


class MedicalMap(models.Model):
    _name = 'medical.map'
    _inherit = 'mail.thread'
    _rec_name = 'code'

    def _compute_start_date(self):
        start_date = datetime.now()
        return start_date

    TYPE = [('surgery', _('Cirurgia')),  # Cirurgia
        ('lab_test', _('Exames')),  # Exames
        ('hospitalization', _(u'Internação')),  # Internação
        ('medical_appointment', _('Consulta')),  # Consulta
        ('medicament', _('Medicamentos')),  # Medicamentos
        ('vaccines', _('Vacinas')),  # Vacinas
        ('attested', _('Atestado')),  # Atestado
        ('specialty', _('Especialidade')),  # Especialidade
        ('esthetics', _('Estetica')),  # Estetica
    ]

    code = fields.Char(string='Code', copy=False, readonly=True)
    name = fields.Selection(string="Type", required=True, selection=TYPE, track_visibility='onchange')
    state = fields.Selection(string="State", default='draft',
        selection=[('draft', _('Draft')),('schedule', _('Schedule')),
            ('start_attendance', _('Start Attendance')), ('pause_attendance', _('Pause Attendance')),
            ('stop_attendance', _('Stop Attendance')), ('pending_payment', _('Pending Payment')),
            ('hospitalized', _('Hospitalized')), ('approved', _('Approved')), ('disapproved', _('Disapproved')),
            #('open', _('Open')),('closed', _('Closed')), ('open_attendance', _('Open Attendance')),
            ('done', _('Done')), ('canceled', _('Canceled'))], track_visibility='onchange')
    start_date = fields.Datetime(string=_("Start Date"), default=_compute_start_date, required=True, track_visibility='onchange')
    end_date = fields.Datetime(string=_("End Date"), track_visibility='onchange')
    sur_building_id = fields.Datetime(string=_("End Date"), track_visibility='onchange')
    building_id = fields.Many2one('medical.hospital.building', string="Building", track_visibility='onchange')
    owner_id = fields.Many2one('res.partner', string='Owner', required=True, domain=[('is_owner', '=', True)], track_visibility='onchange')
    owner_id_invisible = fields.Many2one('res.partner', string='Owner', domain=[('is_owner', '=', True)], track_visibility='onchange')
    start_date = fields.Datetime(string=_("Start Date"), default=_compute_start_date, required=True)
    unpause_date = fields.Datetime(string=_("Unpause Date"), required=False)
    end_date = fields.Datetime(string=_("End Date"))
    sur_building_id = fields.Datetime(string=_("End Date"))
    building_id = fields.Many2one('medical.hospital.building', string="Building")
    owner_id = fields.Many2one('res.partner', string='Owner', required=True, domain=[('is_owner', '=', True)])
    owner_id_invisible = fields.Many2one('res.partner', string='Owner', domain=[('is_owner', '=', True)])
    patient_id = fields.Many2one('medical.patient', string='Patient', required=True,
        domain="[('owner_id', '=', owner_id)]", track_visibility='onchange')
    patient_id_invisible = fields.Many2one('medical.patient', string='Patient', domain="[('owner_id', '=', owner_id)]", track_visibility='onchange')
    doctor_id = fields.Many2one('medical.physician', 'Doctor', track_visibility='onchange')
    pet_age = fields.Char('Patient Age', track_visibility='onchange')
    service_id = fields.Many2one('product.product', string="Service", track_visibility='onchange')
    extra_info = fields.Text(string="Extra Info", track_visibility='onchange')
    observations = fields.Text(string="Observations", track_visibility='onchange')
    # COMPUTED
    price = fields.Float(string="Price", compute='_compute_price', track_visibility='onchange')
    order_id = fields.Many2one('sale.order', string='Quotation', compute='_compute_order_id', track_visibility='onchange')
    # RELATED
    next_step_id = fields.Many2one('medical.next.steps', string='Next Step', track_visibility='onchange')
    admission_id = fields.Many2one('medical.inpatient.registration', string='Admission', track_visibility='onchange')
    sale_order_line_id = fields.Many2one('sale.order.line', 'Order Line', track_visibility='onchange')
    log_ids = fields.One2many('medical.map.log', 'map_id', string="Log", track_visibility='onchange')
    next_activity_id = fields.Many2one('medical.step.activity', string="Next Step", track_visibility='onchange')
    activity_date = fields.Date("Activity Date", track_visibility='onchange')
    type_of_letter_id = fields.Many2one('medical.office.template', string="Type of Letter", track_visibility='onchange')
    vaccine_ids = fields.One2many('medical.map.vaccine', 'map_id', string="Vaccines", track_visibility='onchange')
    step_ids = fields.One2many('medical.map.step', 'map_id', string="Step")
    # Surgery Fields
    sur_pathology_id = fields.Many2one('medical.pathology', 'Base condition', track_visibility='onchange')
    sur_classification = fields.Selection(
        [('optional', _('Optional')), ('required', _('Required')), ('urgent', _('Urgent')),
            ('emergency', _('Emergency')), ], 'Surgery Classification', sort=False, track_visibility='onchange')
    sur_prescription_id = fields.Many2one('medical.prescription.order', string="Prescription",
        domain="[('patient_id', '=', patient_id)]", track_visibility='onchange')
    sur_anesthetist = fields.Many2one('medical.physician', string="Anesthetist",
        domain=[('especiality_anesthesiology', '=', 1)], track_visibility='onchange')
    sur_intercurrences = fields.Text(string="Intercurrences", track_visibility='onchange')
    sur_internal = fields.Char(string="Internal", track_visibility='onchange')
    sur_weight = fields.Char(string="Weight", track_visibility='onchange')
    sur_asa = fields.Char(string="ASA", track_visibility='onchange')
    sur_fc = fields.Char(string="FC", track_visibility='onchange')
    sur_fr = fields.Char(string="FR", track_visibility='onchange')
    sur_ms = fields.Char(string="Mc", track_visibility='onchange')
    sur_hidr = fields.Char(string="Hidr", track_visibility='onchange')
    sur_tc = fields.Char(string="TºC", track_visibility='onchange')
    sur_blood_glucose = fields.Char(string="Blood Glucose", track_visibility='onchange')
    sur_surgery_time = fields.Float(string="Surgery Time", track_visibility='onchange')
    sur_anesthesia_time = fields.Float(string="Anesthesia Time", track_visibility='onchange')
    sur_anesthesy_ids = fields.One2many('medical.map.anesthesy', 'map_id', string="Anesthesys", track_visibility='onchange')
    sur_record_ids = fields.One2many('medical.map.record', 'map_id', string="Records", track_visibility='onchange')
    sur_material_ids = fields.One2many('medical.map.product', 'map_id', string="Materials", track_visibility='onchange')
    sur_office_template_id = fields.Many2one('medical.office.template', string="Clinical Authorization", track_visibility='onchange')
    sur_pre_operator_id = fields.Many2one('medical.office.template', string="Pre Operator",
        domain=[('type', '=', 'surgery')], track_visibility='onchange')
    sur_pos_operator_id = fields.Many2one('medical.office.template', string="Pos Operator",
        domain=[('type', '=', 'surgery')], track_visibility='onchange')
    sur_document = fields.Binary(string="Document", track_visibility='onchange')
    sur_procedure_type_id = fields.Many2one('product.template', string="Surgery Type",
        domain=[("medical_type", "=", "surgery")], track_visibility='onchange')
    sale_approved = fields.Selection([('no_approved', _('Not Approved')), ('approved', _('Approved'))],
        _('Sale Approved'), default='no_approved', track_visibility='onchange')
    schedule_state = fields.Selection([('no_schedule', _('Not Schedule')), ('schedule', _('Schedule'))],
                                      _('Schedule State'), default='no_schedule', track_visibility='onchange')
    schedule_ok = fields.Boolean('schedule ok')

    # Hospitalization Fields
    hospitalization_bed = fields.Many2one('medical.hospital.bed', string="Bed", track_visibility='onchange')
    intensivist_veterinary = fields.Many2one('medical.physician', string="Intensivist",
        domain=[('especiality_intensive_veterinary_medicine', '=', 'True')], track_visibility='onchange')
    hospitalization_services_id = fields.Many2one('product.template', string=_("Services"), track_visibility='onchange')
    monitoring_report_ids = fields.One2many('monitoring.report.line', 'map_id', string=_("Reports"), track_visibility='onchange')
    medical_pathology_ids = fields.One2many('medical.pathology.line', 'map_id', string=_("Pathologys"), track_visibility='onchange')
    medical_diseases_ids = fields.One2many('medical.diseases.line', 'map_id', string=_("Services"), track_visibility='onchange')
    estimated_time = fields.Char(string=_("Estimated Time"), invisible=True)

    # Lab Test Fields
    lab_test_type = fields.Selection(string="Test Type",
        selection=[('image', _("Imagem")), ('laboratory', _("Laboratory"))], track_visibility='onchange')
    lab_external_request_issurance_id = fields.Many2one('medical.office.template', string="Preparatory Information",
        domain=[('type', '=', 'lab_test')], track_visibility='onchange')
    lab_preparatory_information_id = fields.Many2one('medical.office.template', string="Preparatory Information",
        domain=[('type', '=', 'lab_test')], track_visibility='onchange')
    lab_type_of_letters_id = fields.Many2one('medical.office.template', string="Type of letters",
        domain=[('type', '=', 'lab_test')], track_visibility='onchange')
    lab_requester_external = fields.Boolean(string="Is external request?", track_visibility='onchange')
    lab_requester_id = fields.Many2one('medical.physician', string="Requester", track_visibility='onchange')
    lab_partner_clinic_id = fields.Many2one('res.partner', string="Partner Clinic",
        domain=[('is_institution', '=', True)], track_visibility='onchange')
    # Medical Appoitment
    ma_vaccine_line_ids = fields.One2many("vaccines.line", 'map_id', string=_("Vaccines"), track_visibility='onchange')
    ma_anamnesis = fields.Text(string="Anamnesis", track_visibility='onchange')
    ma_food = fields.Text(string="Food", track_visibility='onchange')
    ma_main_complaint = fields.Text(  # Queixa Principal
        string="Main Complaint", track_visibility='onchange')
    ma_prescription = fields.Text(string="Prescription", track_visibility='onchange')
    ma_abdominal_palpation = fields.Text(string="Abdominal Palpation", track_visibility='onchange')
    ma_vaccine = fields.Text(string="Vaccine", track_visibility='onchange')
    ma_weight = fields.Float(string="Weight", track_visibility='onchange')
    ma_body_score = fields.Char(string="Body Score", track_visibility='onchange')
    ma_tc = fields.Char(string="T° C", track_visibility='onchange')
    ma_fr = fields.Char(string="FR", track_visibility='onchange')
    ma_fc = fields.Char(string="FC", track_visibility='onchange')
    ma_tpc = fields.Char(string="TPC", track_visibility='onchange')
    ma_pas = fields.Char(string="PAS", track_visibility='onchange')
    ma_lymph_nodes = fields.Text(string="Lymph Nodes", track_visibility='onchange')
    ma_mucous = fields.Text(string="Mucous", track_visibility='onchange')
    ma_hydratation = fields.Char(string="Hidratation", track_visibility='onchange')
    ma_ectoparasite = fields.Char(string="Ectoparasite", track_visibility='onchange')
    ma_cardiopulmonary_auscultation = fields.Text(string="Cardiopulmonary Auscultation", track_visibility='onchange')
    ma_skin = fields.Text(string="Skin", track_visibility='onchange')
    ma_mouth = fields.Text(string="Mouth", track_visibility='onchange')
    ma_castrated = fields.Boolean(string="Castrated", track_visibility='onchange')
    ma_lameness = fields.Boolean(string="Lameness", track_visibility='onchange')
    ma_patellar_dislocation = fields.Boolean(string="Patellar Dislocation", track_visibility='onchange')
    ma_animal_iris_2 = fields.Boolean(string="Animal IRIS 2", track_visibility='onchange')
    ma_anti_flea_suggested = fields.Boolean(  # Anti Pulgas Sugerido
        string="Anti Flea Suggested", track_visibility='onchange')
    ma_worming = fields.Boolean(string="Suggested Vermifuge", track_visibility='onchange')
    ma_suspected = fields.Boolean(string="Suspected", track_visibility='onchange')
    ma_diagnostic_confirmation = fields.Boolean(string="Diagnostic Confirmation", track_visibility='onchange')
    ma_claudication = fields.Boolean(string="Claudication", track_visibility='onchange')
    ma_pathology_id = fields.Many2one('medical.pathology', string="Pathology", track_visibility='onchange')
    ma_protocol_suggestion_tpl = fields.Many2one('mail.template', string="Protocol Suggestion", track_visibility='onchange')
    ma_office_template_id = fields.Many2one('medical.office.template', string="Type of Letters",
        domain=[('type', '=', 'medical_appointment')], track_visibility='onchange')
    ma_suggested_product_ids = fields.One2many('medical.map.suggested.product', 'map_id', string="Suggested Services", track_visibility='onchange')

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):

        res = super(MedicalMap, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu)

        return res



    @api.one
    @api.constrains('state', 'name', 'owner_id')
    def _check_os(self):
        # args = [('id', '!=', self.id), ('state', '=', 'open'), ('name', '=', self.name),
        args = [('id', '!=', self.id), ('state', '=', 'schedule'), ('name', '=', self.name),
                ('owner_id', '=', self.owner_id.id), ('admission_id', '=', self.admission_id.id)]

        search = self.search(args)
        if search:
            raise ValidationError(
                _("Alredy exist OS type %s opened. [%s]" % (self.name, ",".join(map(lambda x: x.code, search)))))

    @api.onchange('sur_procedure_type_id')
    def onchange_sur_procedure_type_id(self):
        mrp_bom_ids = self.env['mrp.bom'].search([('product_tmpl_id', '=', self.sur_procedure_type_id.id)])
        update_vals = []
        if mrp_bom_ids:
            for line in mrp_bom_ids:
                if line.bom_line_ids:
                    for bom_line in line.bom_line_ids:
                        v = {'map_id': self.id, 'product_id': bom_line.product_id.id, 'quantity': 0, }
                        update_vals.append((0, 0, v))

        self.sur_material_ids = update_vals

    @api.onchange('end_date')
    def onchange_end_date(self):
        if self.end_date:
            if self.end_date < self.start_date:
                raise UserError(_('The end date must be equal or higher than the start date!'))

    @api.multi
    def name_get(self):
        res = []
        for field in self:
            res.append(
                (field.id, _('OS: %s Type: %s') % (field.code, dict(self._fields['name'].selection).get(field.name))))
        return res

    @api.onchange('schedule_state')
    def onchange_schedule_state(self):
        if self.schedule_state == 'schedule':
            self.schedule_ok = True


    @api.multi
    def schedule_appointment(self):
        vals = {
            #'name': 'Appointment %s' % self.code,
            'patient_id': self.patient_id.id,
            'owner_id': self.owner_id.id,
            'doctor_id': self.doctor_id.id,
            'service_type': self.name,
            'appointment_date': self.start_date,
            'appointment_end': self.end_date,
            'building_id': self.building_id.id,
            'medical_procedure_id': self.service_id.id,
            'map_id': self.id,
            'duration':0.5
        }
        res = self.env['medical.appointment'].create(vals)
        res.confirm_scheduled()
        self.write({'schedule_state':'schedule','state':'schedule'})

    @api.onchange('service_id')
    def onchange_service_id(self):
        res = {}
        vals = []
        defaults = []
        res_id = False
        if self._context:
            if self._context.get('params'):
                res_id = self._context.get('params').get('id')
        for p in self.env['medical.map.product'].search([('map_id', '=', res_id)]):
            v = {'product_id': p.product_id.id, }
            defaults.append((1, p.id, v))

        if self.service_id:
            for bom in self.service_id.bom_ids:
                for line in bom.bom_line_ids:
                    v = {'map_id': self.id, 'product_id': line.product_id.id, 'quantity': 0, }
                    vals.append((0, 0, v))
        if vals:
            self.sur_material_ids = vals + defaults
            warning_mess = {'title': _('Warning!'), 'message': _('Material list added %d product(s).' % len(vals)), }
            res = {'warning': warning_mess}
        else:
            self.sur_material_ids = defaults
        return res

    @api.multi
    def refresh_map(self):
        lines_search_p = self.env['medical.diseases.line'].search([('map_id', '=', self.id)])
        for i in lines_search_p:
            i.unlink()
        for lp in self.medical_pathology_ids:
            if lp.suspicion:
                for line in lp.pathology_id.diagnostic_suspicion:
                    v = {
                            'map_id': self.id,
                            'pathology_id': lp.pathology_id.id,
                            'pathology_line_id': lp.id,
                            'suggested_service': line.id,
                        }
                    self.env['medical.diseases.line'].create(v)
            if lp.diagnostic:
                for line in lp.pathology_id.diagnostic:
                    v = {
                            'map_id': self.id,
                            'pathology_id': lp.pathology_id.id,
                            'pathology_line_id': lp.id,
                            'suggested_service': line.id,
                        }
                    self.env['medical.diseases.line'].create(v)

        return True


    # self.env['monitoring.report.line'].search([('monitoring_report_id', '=', self._origin.id)])

    # @api.depends('state_hospitalization')
    # def _onchange_state_hospitalization(self):
    #     if self.state_hospitalization == 'done':
    #         self.end_date = datetime.now()
    #         self.estimated_time = self.end_date - self.start_date

    @api.one
    @api.depends('sale_order_line_id')
    def _compute_order_id(self):
        if self.sale_order_line_id:
            self.order_id = self.sale_order_line_id.order_id.id
        else:
            self.order_id = False

    @api.one
    @api.depends('service_id')
    def _compute_price(self):
        if self.service_id:
            self.price = self.service_id.list_price
        else:
            self.price = 0

    @api.model
    def default_get(self, fields):
        res = super(MedicalMap, self).default_get(fields)
        return res

    @api.model
    def create(self, vals):
        vals['code'] = self.env['ir.sequence'].next_by_code('medical.map_code')
        if 'patient_id_invisible' in vals:
            vals['patient_id'] = vals['patient_id_invisible']
        if 'owner_id_invisible' in vals:
            vals['owner_id'] = vals['owner_id_invisible']
        result = super(MedicalMap, self).create(vals)
        if result.schedule_ok:
            result.schedule_appointment()
        obj_res_partner = self.env['res.partner']

        values = {'origin_id': result.id,
            'next_activity_id': 'next_activity_id' in vals and vals['next_activity_id'] or self.next_activity_id,
            'owner_id': 'owner_id' in vals and vals['owner_id'] or self.owner_id,
            'patient_id': 'patient_id' in vals and vals['patient_id'] or self.patient_id,
            'email': 'owner_id' in vals and obj_res_partner.browse(vals['owner_id']).email or '',
            'phone': 'owner_id' in vals and obj_res_partner.browse(vals['owner_id']).phone or '', }

        if 'activity_date' in vals:
            values.update({'date': vals['activity_date']})

        if 'next_activity_id' in vals or 'activity_date' in vals:
            next_activity_id = self.env['medical.next.steps'].search([('origin_id','=',self.id)])
            if next_activity_id:
                next_activity_id.write(values)
            else:
                next_activity_id = self.env['medical.next.steps'].create(values)

        # self.env['medical.next.steps'].create(values)

        return result

    @api.multi
    def unlink(self):
        for omap in self:
            if omap.admission_id:
                raise UserError(_('The map can not be removed as long as it is associated with an admission'))
        return super(MedicalMap, self).unlink()

    @api.multi
    def render_html(self):
        if self.name == 'medical_appointment':
            res = self.type_of_letter_id.mail_template_id.render_template(
                template_txt=self.type_of_letter_id.mail_template_id.body_html, model='res.partner',
                res_ids=self.owner_id.id)
            return res
        res = self.sur_office_template_id.mail_template_id.render_template(
            template_txt=self.sur_office_template_id.mail_template_id.body_html, model='res.partner',
            res_ids=self.owner_id.id)
        return res

    @api.multi
    def create_monitoring_report(self):
        return {
            'name': _('Create Report'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'medical.monitoring.report',
            'view_id': self.env.ref('hospital_management.medical_monitoring_form').id,
            'context': {
                'default_patient_id': self.patient_id.id,
                'default_doctor_id': self.doctor_id.id,
                'wizard_view': False,
            },
            'target': 'new',
        }

    @api.multi
    def action_draft_quotation(self):
        if self.admission_id.state != 'open':
            raise UserError(_('Start admission to change state.'))
        self.write({'state': 'draft'})
        self.admission_id._compute_amount()

    @api.multi
    def action_start_attendance(self):
        return self.write({'state': 'start_attendance'})

    @api.multi
    def action_pause_attendance(self):
        pause_date = datetime.now()

        start_date = self.start_date

        if pause_date < datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S"):
            raise UserError(_('Pause attendance only after the start date'))
        else:

            if self.unpause_date > start_date:
                start_date = self.unpause_date

            step_vals = {
                'start_date': start_date,
                'pause_date': pause_date,
                # 'info': tbl.encode('utf-8'),
                'map_id': self.id,
                'admission_id': self.admission_id.id
            }
            step_vals = self.env['medical.map.step'].create(step_vals)

            return self.write({'state': 'pause_attendance'})

    @api.multi
    def action_unpause_attendance(self):
        return self.write({
            'state': 'start_attendance',
            'unpause_date': datetime.now()
        })

    @api.multi
    def action_stop_attendance(self):

        accumulated_time = False
        stop_date = datetime.now()
        start_date = self.start_date

        if stop_date < datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S"):
            raise UserError(_('Stop attendance only after the start date'))
        else:

            if self.unpause_date > start_date:
                start_date = self.unpause_date

            step_vals = {
                'start_date': start_date,
                'pause_date': stop_date,
                # 'info': tbl.encode('utf-8'),
                'map_id': self.id,
                'admission_id': self.admission_id.id
            }
            step_vals = self.env['medical.map.step'].create(step_vals)

        if self.admission_id.step_ids:

            for step in self.admission_id.step_ids:
                if not accumulated_time:
                    accumulated_time = datetime.strptime(step.pause_date,
                                                      "%Y-%m-%d %H:%M:%S") - datetime.strptime(step.start_date,
                                                                                               "%Y-%m-%d %H:%M:%S")
                else:
                    accumulated_time = accumulated_time + (datetime.strptime(step.pause_date,
                                                      "%Y-%m-%d %H:%M:%S") - datetime.strptime(step.start_date,
                                                                                               "%Y-%m-%d %H:%M:%S"))

            if accumulated_time:
                self.estimated_time = accumulated_time
                return self.write({'state': 'stop_attendance'})

    @api.multi
    def action_repprove_quotation(self):
        if self.admission_id.state != 'open':
            raise UserError(_('Start admission to change state.'))
        order = self.sale_order_line_id.order_id
        self.sale_order_line_id.unlink()
        self.write({'state': 'disapproved'})
        lines_total = len(order.order_line)
        if not lines_total:
            order.unlink()

    @api.multi
    def action_done(self):
        if self.owner_id.wallet_partner and self.owner_id.trust != 'bad':
            self.state = 'done'
        else:
            if not self.sale_order_line_id.invoice_lines:
                self.state = 'pending_payment'
            else:
                for i in self.sale_order_line_id.invoice_lines:
                    if i.invoice_id.state != 'paid':
                        self.state = 'pending_payment'
                    else:
                        self.state = 'done'  # self.end_date = datetime.now()  # self.estimated_time = datetime.strptime(self.end_date, "%Y-%m-%d %H:%M:%S") - \  #                       datetime.strptime(self.start_date, "%Y-%m-%d %H:%M:%S")

    @api.multi
    def action_schedule(self):
        if self.sur_office_template_id:
            if not self.sur_document and self.name == 'surgery':
                raise UserError(_("Clinical authorization requires a document attachment"))
            self.state = 'schedule'
            return {'type': 'ir.actions.report.xml', 'report_name': 'hospital_management.report_template_office',
                'report_type': 'qweb-html', 'name': _('Clinical Authorization'),
                'string': _('clinical-authorization-%s' % self.code)}
        else:
            self.state = 'schedule'

    # @api.multi
    # def action_open(self):
    #     # Se tiver autorização clínica, verificar se tem anexos e imprimir autorização
    #     if self.sur_office_template_id:
    #         if not self.sur_document and self.name == 'surgery':
    #             raise UserError(_("Clinical authorization requires a document attachment"))
    #         self.state = 'open'
    #         return {'type': 'ir.actions.report.xml', 'report_name': 'hospital_management.report_template_office',
    #             'report_type': 'qweb-html', 'name': _('Clinical Authorization'),
    #             'string': _('clinical-authorization-%s' % self.code)}
    #     else:
    #         self.state = 'open'

    @api.multi
    def action_open_quotation(self):
        return {"type": "ir.actions.act_window", "res_model": "sale.order", "views": [[False, "form"]],
            "res_id": self.sale_order_line_id.order_id.id, "context": {"create": False, "show_sale": True}, }

    @api.multi
    def write(self, vals):
        res = super(MedicalMap, self).write(vals)
        if self.name == 'hospitalization' or self.name == 'medical_appointment':
            self.refresh_map()
        obj_res_partner = self.env['res.partner']

        values = {'origin_id': self.id,
                  'next_activity_id': 'next_activity_id' in vals and vals['next_activity_id'] or self.next_activity_id.id,
                  'owner_id': 'owner_id' in vals and vals['owner_id'] or self.owner_id.id,
                  'patient_id': 'patient_id' in vals and vals['patient_id'] or self.patient_id.id,
                  'email': 'owner_id' in vals and obj_res_partner.browse(vals['owner_id']).email or '',
                  'phone': 'owner_id' in vals and obj_res_partner.browse(vals['owner_id']).phone or '', }

        if 'activity_date' in vals:
            values.update({'date': vals['activity_date']})

        if 'next_activity_id' in vals or 'activity_date' in vals:
            next_activity_id = self.env['medical.next.steps'].search([('origin_id', '=', self.id)])
            if next_activity_id:
                next_activity_id.write(values)
            else:
                next_activity_id = self.env['medical.next.steps'].create(values)

        body = _('Updated fields: <ul>')
        for key, val in vals.items():
            field_label = self._fields[key].string
            field_translation = self.env['ir.translation'].search(
                [('src', '=', field_label), ('lang', '=', self.env.user.lang)])
            # if 'name' in self[key] or self[key].name:
            #     text = self[key].name
            # elif 'ids' in self[key] or self[key].ids:
            #     text = 'IDs' + self[key].ids
            # elif 'id' in self[key] or self[key].id:
            #     text = 'ID' + self[key].id
            # else:
            text = val

            # if 'name' in self[key]:
            #     text = self[key].name
            # elif 'ids' in self[key]:
            #     text = 'IDs ' + str(self[key].ids).replace("[","").replace("]","")
            # else:
            #     text = val

            if field_translation:
                body += '<li><b>%s</b>: %s</li>' % (field_translation[0].value, text)
            else:
                body += '<li><b>%s</b>: %s</li>' % (field_label, text)

        body += '</ul>'
        # self.message_post(body=body, subject=_("Records Updated"))

        if vals:
            tbl = u"""<table style="border: 1px solid black;">
                       <tr>
                         <th colspan="2" style="text-align: center;">OS: %s </th>
                       </tr>""" % self.code
            fields_get = self.fields_get()
            for key, value in vals.iteritems():
                value = '' if not value else value
                if fields_get.get(key).get('type') == 'text':
                    value = value.replace('\n', '</br>')
                fname = fields_get.get(key).get('string')
                tbl += u"""<tr style="border: 1px solid black;">
                <th style="border: 1px solid black; padding-left: 4px; padding-right: 4px;">{}</th>
                <th style="border: 1px solid black; padding-left: 4px; padding-right: 4px;"><p>{}</p></th>
                </tr>""".format(fname, value)
            tbl += u"""</table>"""
            log_vals = {
                'create_date': datetime.now(),
                'info': tbl.encode('utf-8'),
                'map_id': self.id,
                'admission_id': self.admission_id.id
            }
            log_id = self.env['medical.map.log'].create(log_vals)

        return res


class MedicalMapVaccine(models.Model):
    _name = 'medical.map.vaccine'
    _rec_name = 'vaccine_id'

    map_id = fields.Many2one('medical.map', string="Map", required=True)
    vaccine_id = fields.Many2one('product.template', string="Service", domain="[('medical_type', '=', 'vaccines')]",
        required=True)
    application_date = fields.Date(string="Application Date", required=True)
    dose = fields.Char(string="")
    next_application_date = fields.Date(string="Next Application Date")


class MedicalMapSuggestedProduct(models.Model):
    _name = 'medical.map.suggested.product'
    _rec_name = 'product_id'
    _sql_constraints = [('unique_peoduct', 'UNIQUE(map_id,product_id)', 'Product must be unique')]

    map_id = fields.Many2one('medical.map', string="Map", required=True)
    product_id = fields.Many2one('product.template', string="Product/Service", required=True)


class MedicalMapAnesthesia(models.Model):
    _name = 'medical.map.anesthesy'

    name = fields.Selection(string="Type", required=True,
        selection=[('mma', 'MMA'), ('maintenance', 'Maintenance'), ('induction', 'Induction'), ('others', 'Others')])
    service_id = fields.Many2one('product.product', string="Service", domain="[('type', '=', 'service')]", )
    dose = fields.Char(string="Dose")
    via = fields.Char(string="via")
    date = fields.Datetime(string="Date")
    map_id = fields.Many2one('medical.map', string="Map")


class MedicalMapRecord(models.Model):
    _name = 'medical.map.record'

    date = fields.Datetime(string="Date", required=True)
    service_id = fields.Many2one('product.product', string="Service", domain="[('type', '=', 'service')]", )
    name = fields.Char(string="FC")
    fr = fields.Char(string="FR")
    spo2 = fields.Char(string="SpO2")
    pa = fields.Char(string="PA")
    tc = fields.Char(string="T°C")
    map_id = fields.Many2one('medical.map', string="Map")


class MedicalMapProduct(models.Model):
    _name = 'medical.map.product'

    map_id = fields.Many2one('medical.map', string="Map", required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string="Product", track_visibility='onchange')
    quantity = fields.Integer(string="Quantity", required=True, track_visibility='onchange')


class MedicalMapLog(models.Model):
    _name = 'medical.map.log'

    create_date = fields.Datetime('Create Date', readonly=True)
    map_id = fields.Many2one('medical.map', string="Map", required=True, ondelete='cascade')
    admission_id = fields.Many2one('medical.inpatient.registration', string="Admission", ondelete='cascade')
    info = fields.Text(string="Information", required=True)

class MedicalMapStep(models.Model):
    _name = 'medical.map.step'

    info = fields.Text(string="Information", required=False)
    start_date = fields.Datetime('Start Date', readonly=True)
    pause_date = fields.Datetime('Pause Date', readonly=True)
    map_id = fields.Many2one('medical.map', string="Map", required=True, ondelete='cascade')
    admission_id = fields.Many2one('medical.inpatient.registration', string="Admission", ondelete='cascade')
