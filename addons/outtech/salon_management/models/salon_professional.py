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
import pytz
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_TIME_FORMAT
from datetime import datetime

WEEKDAYS = [
    ('0', _("Monday")),
    ('1', _("Tuesday")),
    ('2', _("Wednesday")),
    ('3', _("Thursday")),
    ('4', _("Friday")),
    ('5', _("Saturday")),
    ('6', _("Sunday"))
]

MONTHS = [
    (1, _("January")),
    (2, _("February")),
    (3, _("March")),
    (4, _("April")),
    (5, _("May")),
    (6, _("June")),
    (7, _("July")),
    (8, _("August")),
    (9, _("September")),
    (10, _("October")),
    (11, _("November")),
    (12, _("December"))
]


class SalonProfessional(models.Model):
    _name = "salon.professional"

    name = fields.Many2one( 'res.users', 'User' )
    info = fields.Text('Extra Info')

    schedule_ids = fields.One2many(
        'salon.professional.schedules', inverse_name='professional_id', string=_("Schedule Times")
    )
    canceled_ids = fields.One2many(
        'salon.professional.canceled', inverse_name='professional_id', string=_("Schedule Canceled")
    )
    especiality_groomer = fields.Boolean(
        string="Groomer"
    )
    especiality_bather = fields.Boolean(
        string="Bather"
    )


    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        res = super(SalonProfessional, self).name_search(name=name, args=args, operator=operator, limit=100)
        return res


class SalonProfessionalSchedule(models.Model):
    _name = 'salon.professional.schedules'
    _rec_name = 'professional_id'

    weekday = fields.Selection(
        string="Weekday", required=True, selection=WEEKDAYS
    )
    month = fields.Selection(
        string="Month", required=True, selection=MONTHS
    )
    year = fields.Integer(
        string="Year", required=True
    )
    start_hour = fields.Float(
        string="Start Hour", required=True
    )
    end_hour = fields.Float(
        string="End Hour", required=True
    )
    professional_id = fields.Many2one(
        'salon.professional', string=_("Professional")
    )


class SalonProfessionalCanceled(models.Model):
    _name = 'salon.professional.canceled'
    _rec_name = 'professional_id'

    date_start = fields.Datetime(
        string=_("Date Start"), required=True
    )
    date_end = fields.Datetime(
        string=_("End Date"), required=True
    )
    professional_id = fields.Many2one(
        'salon.professional', string=_("Professional")
    )

