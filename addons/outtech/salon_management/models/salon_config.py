# -*- coding: utf-8 -*-
##############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2015-TODAY Cybrosys Technologies(<http://www.cybrosys.com>).
#    Author: Avinash Nk(<http://www.cybrosys.com>)
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import models, fields, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    salon_allowed = fields.Boolean(
        string="Salon Allowed"
    )


class SalonWorkingHours(models.Model):
    _name = 'salon.working.hours'

    name = fields.Char(string="Name")
    from_time = fields.Float(string="Starting Time")
    to_time = fields.Float(string="Closing Time")


class SalonHoliday(models.Model):
    _name = 'salon.holiday'

    name = fields.Char(string="Name")
    holiday = fields.Boolean(string="Holiday")


class WorkshopSetting(models.Model):
    _name = "salon.config.settings"

    @api.model
    def booking_chairs(self):
        return self.env['salon.chair'].search([('active_booking_chairs', '=', True)])

    @api.model
    def holidays(self):
        return self.env['salon.holiday'].search([('holiday', '=', True)])

    @api.model
    def allowed_companys(self):
        return self.env['res.company'].search([('salon_allowed', '=', True)])

    salon_booking_chairs = fields.Many2many('salon.chair', string="Booking Chairs", default=booking_chairs)
    allowed_companies_ids = fields.Many2many('res.company', string="Allowed companies", default=allowed_companys)
    salon_holidays = fields.Many2many('salon.holiday', string="Holidays", default=holidays)

    @api.multi
    def execute(self):
        salon_chair_obj = self.env['salon.chair'].search([])
        book_chair = []
        for chairs in self.salon_booking_chairs:
            book_chair.append(chairs.id)
        for records in salon_chair_obj:
            if records.id in book_chair:
                records.active_booking_chairs = True
            else:
                records.active_booking_chairs = False

        salon_holiday_obj = self.env['salon.holiday'].search([])
        holiday = []
        for days in self.salon_holidays:
            holiday.append(days.id)
        for records in salon_holiday_obj:
            if records.id in holiday:
                records.holiday = True
            else:
                records.holiday = False

        allowed_companies_obj = self.env['res.company'].search([])
        allowed_companies = []
        for company in self.allowed_companies_ids:
            allowed_companies.append(company.id)

        for records in allowed_companies_obj:
            print '*** rec', records
            if records.id in allowed_companies:
                records.salon_allowed = True
            else:
                records.salon_allowed = False