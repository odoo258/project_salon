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


class appointment_find_doctor_wizard(models.TransientModel):
    _name = "appointment.find.doctor.wizard"

    phy_id = fields.Many2one('medical.physician', 'Name Of Physician',
                             track_visibility='onchange', required=True)
    date_start = fields.Datetime("Start Date", track_visibility='onchange', required=True)
    date_end = fields.Datetime('End Date')


    @api.onchange('phy_id')
    def onchange_doctor(self):
        if self.phy_id and self.date_start:
            availabilities_ids = self.env['medical.physician.schedules.available'].search(
                [('doctor_id', '=', self.phy_id.id)])

            if len(availabilities_ids) < 1:
                pass
                # if self.phy_id:
                #     args = [
                #         ('doctor_id', '=', self.phy_id.id),
                #         ('appointment_date', '>=', self.date_start),
                #         ('appointment_end', '<=', self.date_end),
                #     ]
                #     search = self.env['medical.appointment'].search(args, limit=1)
                #     if not search:
                #         print "HORA VAGA CRIAR available"
                #
                #     args = [
                #         ('doctor_id', '=', self.doctor_id.id),
                #         ('date_start', '<=', self.appointment_end),
                #         ('date_end', '>=', self.appointment_date)
                #     ]
                #     appointment_date = fields.Datetime.context_timestamp(
                #         self, fields.Datetime.from_string(self.appointment_date)
                #     )
                #     appointment_end = fields.Datetime.context_timestamp(
                #         self, fields.Datetime.from_string(self.appointment_end)
                #     )
                #     if self.env['medical.physician.schedules.canceled'].search(args, limit=1):
                #         raise ValidationError(
                #             _("The veterinarian does not have available hours on this date. (Canceled).")
                #         )
                #     args = [
                #         ('doctor_id', '=', self.doctor_id.id),
                #         ('weekday', '=', str(appointment_date.weekday())),
                #         ('month', '=', appointment_date.month),
                #         ('year', '=', appointment_date.year),
                #         ('start_hour', '<=', appointment_date.hour + (appointment_date.minute * 60 / 3600.)),
                #         ('end_hour', '>=', appointment_end.hour + (appointment_end.minute * 60 / 3600.)),
                #     ]
                #     if not self.env['medical.physician.schedules'].search(args, limit=1):
                #         raise ValidationError(
                #             _("The veterinarian does not have available hours on this date. (Schedules).")
                #         )


    @api.multi
    def show_record(self):

        res = {}
        list_of_ids =[]
        medical_availables_obj = self.env['medical.physician.schedules.available'].search([('doctor_id', '=', self.phy_id.id)])
        for id in medical_availables_obj:
            list_of_ids.append(id.id)
        res = self.env['ir.actions.act_window'].for_xml_id('hospital_management', 'medical_physician_schedules_available_action')
        res['domain'] = "[('id','in',%s)]" % list_of_ids
        res['target'] = "new"
        res['context'] = {'doctor_id': self.phy_id.id}
        return res

    @api.multi
    def cancel(self):
        return {'type': 'ir.actions.act_window_close'}
