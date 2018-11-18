# coding=utf-8
# Author: Christian Douglas <christian.douglas.alcantara@gmail.com>
from odoo import models, fields, api


class SalonOrder(models.Model):
    _inherit = 'salon.order'

    patient_id = fields.Many2one(
        'medical.patient', string="Patient"
    )

    @api.onchange('partner_id')
    def _onchange_partner(self):
        self.patient_id = False


class SalonBookingBackend(models.Model):
    _inherit = 'salon.booking'

    patient_id = fields.Many2one(
        'medical.patient', string="Patient"
    )

    @api.onchange('partner_id')
    def _onchange_partner(self):
        self.patient_id = False

    @api.multi
    def booking_confirm_scheduling(self):
        super(SalonBookingBackend, self).booking_confirm_scheduling()
        if self.patient_id:
            for order in self.filtered_orders:
                order.patient_id = self.patient_id

    @api.multi
    def write(self, vals):
        res = super(SalonBookingBackend, self).write(vals)
        company_id = self.env['res.company']._company_default_get()
        print 'COMPANY ID ***', company_id
        return res
