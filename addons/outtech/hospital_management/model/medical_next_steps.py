# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2017 - OutTech (<http://www.outtech.com.br>).
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

from odoo import models, fields, api, _

class MedicalNextSteps(models.Model):
    _name = "medical.next.steps"
    _inherit = ['mail.thread']

    name = fields.Char(string="Name", readonly=True)
    status = fields.Selection([('opened', 'Opened'), ('done', 'Done'), ('canceled', 'Canceled')], string="Status", default="opened")
    origin_id = fields.Many2one('medical.map', string="Request Origin")
    next_activity_id = fields.Many2one('medical.step.activity', string="Next Activity")
    subject = fields.Char(string="Subject", readonly=True)
    patient_id = fields.Many2one('medical.patient', string="PET")
    owner_id = fields.Many2one('res.partner', domain=[('is_owner', '=', True)], string="Owner")
    email = fields.Char(string="E-mail")
    phone = fields.Char(string="Phone")
    date = fields.Date(string="Date")
    made_by = fields.Many2one('res.users', string="Made By", default= lambda self: self.env.user)
    team_id = fields.Many2one('medical.team', string="Team")
    additional_informations = fields.Text(string="Additional Informations")
    first_activity = fields.Boolean(string="First Activity", default=False)


    @api.model
    def create(self, values):

        if not values:
            values = {}

        values[u'name'] = self.env['ir.sequence'].next_by_code('next_steps_sequence') or _('New')

        return super(MedicalNextSteps, self).create(values)

    @api.onchange('owner_id')
    def _onchange_owner_id(self):

        if self.owner_id:
            self.email = self.owner_id.email
            self.phone = self.owner_id.phone
        else:
            self.email = ''
            self.phone = ''


    @api.multi
    def finalize_next_step(self):

        for log in self:
            body_html = _("<div><b>Change state</b>:</div> %(state_current)s -> %(new_state)s") % {
                'state_current': _('Opened'),
                'new_state': _('Done'),
            }
            log.message_post(body_html, subject=log.subject, subtype_id='')

            log.write({
                'date': log.date,
                'title_action': False,
                'date_action': False,
                'next_activity_id': False,
            })

            log.status = 'done'

        return True

    @api.multi
    def action_register_activity(self):

        view_id = self.env.ref('hospital_management.view_register_activity_form')
        return {
            'name': _('Register Activity'),
            'res_model': 'medical.register.activity',
            'context': {
                'default_next_activity_id': self.next_activity_id.id or "",
                'default_subject': self.subject or "",
                'default_date': self.date or "",
            },
            'type': 'ir.actions.act_window',
            'view_id': False,
            'views': [(view_id.id, 'form')],
            'view_mode': 'form',
            'target': 'new',
            'view_type': 'form',
            'res_id': False
        }

class MedicalRegisterActivity(models.TransientModel):
    _name = "medical.register.activity"

    @api.model
    def _default_next_step_id(self):
        if '_default_next_step_id' in self._context:
            return self._context['_default_next_step_id']
        if self._context.get('active_model') == 'medical.next.steps':
            return self._context.get('active_id')
        return False

    next_activity_id = fields.Many2one('medical.step.activity', string="Activity")
    subject = fields.Char(string="Subject")
    next_step_id = fields.Many2one('medical.next.steps', string='Next_Step', required=True, default=_default_next_step_id)
    date = fields.Date(string="Date")
    note = fields.Html(string="Note")

    @api.multi
    def register_activity(self):

        for log in self:
            body_html = "<div><b>%(title)s</b>: %(next_activity)s</div>%(description)s%(note)s" % {
                'title': _('Activity Done'),
                'next_activity': log.next_activity_id.name,
                'description': log.subject and '<p><em>%s</em></p>' % log.subject or '',
                'note': log.note or '',
            }
            log.next_step_id.message_post(body_html, subject=log.subject, subtype_id='')

            log.next_step_id.write({
                'date': log.date,
                'title_action': False,
                'date_action': False,
                'next_activity_id': False,
            })

            log.next_step_id.first_activity = True

        return True

    @api.multi
    def register_activity_and_schedule(self):
        self.ensure_one()
        self.register_activity()
        view_id = self.env.ref('hospital_management.view_new_register_activity_form')
        return {
            'name': _('New Register Activity'),
            'res_model': 'medical.new.register.activity',
            'context': {
                'default_last_activity_id': self.next_activity_id.id,
                'default_next_step_id': self.next_step_id.id
            },
            'type': 'ir.actions.act_window',
            'view_id': False,
            'views': [(view_id.id, 'form')],
            'view_mode': 'form',
            'target': 'new',
            'view_type': 'form',
            'res_id': False
        }

class MedicalNewRegisterActivity(models.TransientModel):
    _name = "medical.new.register.activity"

    next_activity_id = fields.Many2one('medical.step.activity', string="Activity")
    subject = fields.Char(string="Subject")
    date = fields.Date(string="Date")
    next_step_id = fields.Many2one('medical.next.steps', string='Next_Step')

    @api.multi
    def new_register_activity(self):

        vals = {
            'next_activity_id': self.next_activity_id.id,
            'date': self.date,
            'subject': self.subject,
        }

        self.next_step_id.write(vals)

        return True


class CancellationNextStep(models.TransientModel):
    _name = "cancellation.next.step"

    @api.model
    def _default_next_step_id(self):
        if '_default_next_step_id' in self._context:
            return self._context['_default_next_step_id']
        if self._context.get('active_model') == 'medical.next.steps':
            return self._context.get('active_id')
        return False

    reason_id = fields.Many2one('medical.cancellation.reasons', string="Reason")
    next_step_id = fields.Many2one('medical.next.steps', string='Next_Step', default=_default_next_step_id)
    other = fields.Boolean(string="Other", default=False)
    other_reason = fields.Text(string="Reason")

    @api.multi
    def cancel_next_step(self):

        for log in self.next_step_id:
            body_html = _("<div><b>Change State</b>:</div> %(state_current)s -> %(new_state)s <div><b>Reason</b>:</div> %(reason)s") % {
                'state_current': _('Opened'),
                'new_state': _('Canceled'),
                'reason': self.reason_id.name or _('None'),
            }
            log.message_post(body_html, subject=log.subject, subtype_id='')

            log.write({
                'date': log.date,
                'title_action': False,
                'date_action': False,
                'next_activity_id': False,
            })

            self.next_step_id.write({'status': 'canceled'})

        return {'type': 'ir.actions.act_window_close'}

class MedicalCancellationReasons(models.Model):
    _name = "medical.cancellation.reasons"

    name = fields.Char(string="Description", required=True)
    active = fields.Boolean(string="Active", default=False)

class MedicalStepActivity(models.Model):
    _name = "medical.step.activity"

    name = fields.Char(string="Name", required=True)
    team_id = fields.Many2one('medical.team', string="Team")
    description = fields.Text(string="Description")

class MedicalTeam(models.Model):
    _name = "medical.team"

    name = fields.Char(string="Name", required=True)
    use_appointment = fields.Boolean(string="Use Appointment", default=False)
    use_admission = fields.Boolean(string="Use Admission", default=False)
    use_map = fields.Boolean(string="Use Map", default=False)
    res_user_ids = fields.Many2many('res.users', 'team_user_rel', 'team_id', 'user_id', string="Members")

class ResUsers(models.Model):
    _inherit = "res.users"

    team_id = fields.Many2one('medical.team', string="Team")