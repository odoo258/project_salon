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
from odoo import api, fields, models, _


class appointment_wizard(models.TransientModel):
    _name = "appointment.wizard"

    phy_id = fields.Many2one('medical.physician',string="Name Of Physician")
    a_date = fields.Date('Appointment Date')
    
    @api.multi
    def show_record(self):
        res = {}
        list_of_ids =[]
        appointment_obj = self.env['medical.appointment'].search([('doctor_id','=',self.phy_id.id),('appointment_date','=',self.a_date)])
        for id in appointment_obj:
            list_of_ids.append(id.id)
        res = self.env['ir.actions.act_window'].for_xml_id('hospital_management', 'action_medical_appointment')
        res['domain'] = "[('id','in',%s)]" % list_of_ids
        return res
    

class AppointmentCancelWizard(models.TransientModel):
    _name = 'appointment.cancel.wizard'
    REASONS = [
        ('abandonment', 'Abandonment'),
        ('price', 'Price'),
        ('reschedule', 'Reschedule'),
        ('personal-problem', 'Personal Problem'),
        ('other', 'Other')
    ]
    reason_for_cancellation = fields.Selection(
        string="Reason for Cancellation", selection=REASONS, required=True
    )
    observation_cancellation = fields.Text(
        string="Observation"
    )

    @api.multi
    def confirm(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        for record in self.env['medical.appointment'].browse(active_ids):
            record.state = 'canceled'
            record.reason_for_cancellation = self.reason_for_cancellation
            record.observation_cancellation = self.observation_cancellation
        #self.env.user.notify_warning('My information message', sticky=True)
        return {'type': 'ir.actions.act_window_close'}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: