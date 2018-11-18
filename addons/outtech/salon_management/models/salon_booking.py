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
from datetime import date, datetime, timedelta


class SalonBookingBackend(models.Model):
    _name = 'salon.booking'

    name = fields.Char(string="Number")
    partner_id = fields.Many2one(
        'res.partner', string='Partner', required=True
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], default="draft")
    time = fields.Datetime(string="Date")
    end_date = fields.Datetime(string="End Date", compute='_compute_end_date', store=True)
    phone = fields.Char(string="Phone")
    email = fields.Char(string="E-Mail")
    services = fields.Many2many(
        'product.template', string="Services", domain=[('type', '=', 'service')], required=True
    )
    chair_id = fields.Many2one('salon.chair', string="Chair", required=True)
    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env['res.company'].browse(1))
    # lang = fields.Many2one('res.lang', 'Language',
    #                        default=lambda self: self.env['res.lang'].browse(1))
    professional_id = fields.Many2one('salon.professional', string='Professional', required=True)

    @api.depends('time', 'services')
    def _compute_end_date(self):
        dt = datetime.strptime(self.time, "%Y-%m-%d %H:%M:%S")
        for service in self.services:
            duration = service.time_taken
            if duration:
                dt = dt + timedelta(hours=duration)
        self.end_date = dt

    @api.onchange('partner_id')
    def _onchange_partner(self):
        if self.partner_id:
            self.email = self.partner_id.email
            self.phone = self.partner_id.phone or self.partner_id.mobile
        else:
            self.email = False
            self.phone = False

    def all_salon_orders(self):
        if self.time:
            date_only = str(self.time)[0:10]
        else:
            date_only = date.today()
        all_salon_service_obj = self.env['salon.order'].search([('chair_id', '=', self.chair_id.id),
                                                                ('start_date_only', '=', date_only)])
        self.filtered_orders = [(6, 0, [x.id for x in all_salon_service_obj])]

    filtered_orders = fields.Many2many('salon.order', string="Salon Orders", compute="all_salon_orders")

    @api.multi
    def booking_approve(self):
        salon_order_obj = self.env['salon.order']
        salon_service_obj = self.env['salon.order.lines']
        order_data = {
            'partner_id': self.partner_id.id,
            # 'patient_id': self.patient_id.id,
            'chair_id': self.chair_id.id,
            'start_time': self.time,
            'date': date.today(),
            'stage_id': 1,
            'booking_identifier': True,
        }
        order = salon_order_obj.create(order_data)
        for records in self.services:
            service_data = {
                'service_id': records.id,
                'time_taken': 0,  # records.time_taken
                'price': records.list_price,
                'price_subtotal': records.list_price,
                'salon_order': order.id,
            }
            salon_service_obj.create(service_data)
        template = self.env.ref('salon_management.salon_email_template_approved')
        self.env['mail.template'].browse(template.id).send_mail(self.id)
        self.state = "approved"

    @api.multi
    def booking_reject(self):
        template = self.env.ref('salon_management.salon_email_template_rejected')
        self.env['mail.template'].browse(template.id).send_mail(self.id)
        self.state = "rejected"

    @api.model
    def create(self, vals):
        res = super(SalonBookingBackend, self).create(vals)
        res.name = 'RES{:04d}'.format(res.ids[0])
        return res

class SalonCancelBooking(models.Model):
    _name = 'salon.cancel.booking'

    REASONS = [('abandonment', 'Abandonment'), ('price', 'Price'), ('reschedule', 'Reschedule'),
        ('personal-problem', 'Personal Problem'), ('other', 'Other')]

    reason_for_cancellation = fields.Selection(string="Reason for Cancellation", selection=REASONS, required=True)
    observation_cancellation = fields.Text(string="Observation")

    @api.multi
    def confirm(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        for record in self.env['salon.booking'].browse(active_ids):
            record.state = 'rejected'
            record.reason_for_cancellation = self.reason_for_cancellation
            record.observation_cancellation = self.observation_cancellation
        # self.env.user.notify_warning('My information message', sticky=True)
        return {'type': 'ir.actions.act_window_close'}
