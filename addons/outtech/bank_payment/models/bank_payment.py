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

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError

class BankPayment(models.Model):
    _name = 'bank.payment'

    @api.multi
    def unlink(self):

        for bank_payment in self:
            if bank_payment.status == 'paid':
                raise UserError(_('Error! Is not possible delete bank payment(s) paid!'))

        return super(BankPayment, self).unlink()

    def get_file(self):

        obj_ir_attachment = self.pool.get('ir.attachment')

        res = {}
        for record in self.read():

            res[record['id']] = False

            src_ir_attachment = obj_ir_attachment.search([('res_model', '=', 'bank.payment'), ('res_id', '=', record['id'])])

            if src_ir_attachment:
                file_data = obj_ir_attachment._data_get(src_ir_attachment)

                if file_data:
                    res[record['id']] = file_data[src_ir_attachment[0]]

        return res

    # def cancel_bank_payment(self, cr, uid, ids, context=None):
    #
    #     for br_bank_payment in self.browse(cr, uid, ids):
    #
    #         if br_bank_payment.status not in ('open', 'confirmed'):
    #             raise orm.except_orm(_('Error!'), _('The bank payment, is already paid or canceled!'))
    #
    #         for invoice_lines in br_bank_payment.invoice_installment_ids:
    #             self.pool.get('account.move.line').write(cr, uid, invoice_lines.id, {'bank_payment_id': ''})
    #
    #         self.write(cr, uid, br_bank_payment.id, {'status': 'canceled'})


    name = fields.Char(string='Code', readonly=True)
    date_maturity = fields.Date(string='Date Maturity', readonly=True)
    date_create = fields.Date(string='Date Create', digits_compute=dp.get_precision('Account'), readonly=True)
    payment_mode_id = fields.Many2one('payment.mode', string="Payment Mode", readonly=True)
    partner_id = fields.Many2one('res.partner', string='Partner', readonly=True)
    company_id = fields.Many2one('res.company', string='Company', readonly=True)
    bank_slip_file = fields.Binary(default=get_file, string='Bank Slip File', readonly=True)
    filename = fields.Char('Filename', size=128)
    our_number = fields.Char(string='Our Number', readonly=True)
    value = fields.Float(string='Value', readonly=True)
    value_paid = fields.Float(string='Value Paid', readonly=True)
    invoice_installment_ids = fields.One2many('account.move.line', 'bank_payment_id', string='Invoice Installments', readonly=True)
    status = fields.Selection([('open', 'Open'), ('confirmed', 'Confirmed'), ('paid', 'Paid'), ('canceled', 'Canceled')], string='Status', default='open', readonly=True)