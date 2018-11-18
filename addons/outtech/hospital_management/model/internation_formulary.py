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


class internationformulary(models.Model):
    _name = 'internation.formulary'


    type_id = fields.Char(string='Type', required=True, readonly=True,
                       default='Internation')


    owner_id = fields.Many2one(
        'res.partner', string="Owner", required=True, domain=[('is_owner', '=', True)]
    )

    patient = fields.Many2one(
        'medical.patient', string="Pet", required=True, domain="[('owner_id', '=', owner_id)]"
    )

    bed = fields.Many2one('medical.hospital.bed', string="Hospital Bed"
    )

    attending_physician = fields.Many2one('medical.physician', string="Attending Physician")

    operating_physician = fields.Many2one('medical.physician', string="Operating Physician")

    service_id = fields.Many2one(
        'product.product', string="Service", domain=[('type', '=', 'service')]
    )

    hospitalization_date = fields.Datetime(
        string="Hospitalization date", required=True)

    discharge_date = fields.Datetime(
        string="Expected Discharge date"
    )

    state = fields.Selection([
        ('open', 'Open'),
        ('in_process', 'In Process'),
        ('waiting_payment', 'Waiting Payment'),
        ('done', 'done'),]
    , string='Status', readonly=True,   default='open')

    def check_admission(self):
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
            _logger.debug("Admission Count: {} - Args: {}".format(admissions_count, args))
            if admissions_count:
                for user in self.env['res.users'].browse(eval(users)):
                    _logger.debug(u"Notify user: {}".format(user.name))
                    user.notify_warning(
                        message=_(
                            "%02d patient(s) waiting for care <a style='color: black' href='/web#min=1&limit=80&"
                            "view_type=list&model=medical.inpatient.registration&action=%d' class='pull-right'>"
                            "GO <i class='fa fa-external-link'></i></a>" % (admissions_count, xml_id.get('id'))
                        ), sticky=True
                    )



