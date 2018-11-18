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

from odoo import fields, models, _
from datetime import date
from odoo.exceptions import UserError

class BankPaymentCreate(models.Model):
    _name = 'bank.payment.create'

    def _validate_lines(self):

        first_line = False

        for rec_account_move_line in self.ids:

            if not first_line:

                vals = {
                    'date_maturity': rec_account_move_line.date_maturity,
                    'payment_type': rec_account_move_line.payment_type.id,
                    'partner_id': rec_account_move_line.partner_id.id,
                    'company_id': rec_account_move_line.company_id.id,
                    'invoice_id': rec_account_move_line.invoice.id
                    }

                first_line = True

            else:
                if rec_account_move_line.date_maturity != vals['date_maturity']:
                    return False, False
                if rec_account_move_line.payment_type.id != vals['payment_type']:
                    return False, False
                if rec_account_move_line.partner_id.id != vals['partner_id']:
                    return False, False
                if rec_account_move_line.company_id.id != vals['company_id']:
                    return False, False


        return True

    def our_number_choose(self, cod_bank):

        if cod_bank == '033':
            return 'bank_payment_our_number_santander'
        else:
            UserError(_('Error: Do not have our_number sequence for this bank!'))


    def create_bank_payment(self):

        obj_bank_payment = self.env['bank.payment']
        obj_account_move_line = self.env['account.move.line']

        if self.join_installment:

            res = self._validate_lines()
            if not res:
                raise UserError(_('Error! The lines have different data to create a single bank payment'))

            br_account_move_line = obj_account_move_line.browse(self.ids)

            if br_account_move_line.payment_type.generate_bank_payment != True:
                raise UserError(_('Error! The payment type not have permission to create bank payments'))

            vals = {
                    'name': self.pool.get('ir.sequence').get('bank_slip_code_sequence'),
                    'date_maturity': br_account_move_line.date_maturity,
                    'date_create': date.today(),
                    'payment_type_id': br_account_move_line.payment_type.id,
                    'partner_id': br_account_move_line.partner_id.id,
                    'company_id': br_account_move_line.company_id.id,
                    'status': 'open'
                }

            bank_payment_id = obj_bank_payment.create(cr, uid, vals)

            value_total = 0.0

            for rec_account_move_line in obj_account_move_line.browse(cr, uid, context['active_ids'], context=context):

                if rec_account_move_line.bank_payment_id:
                    raise UserError(_('Error! Exist installment(s), related already with a bank payment(s), please cancel the bank payment(s), to can generate new(s) bank payment(s)!'))

                value_total += rec_account_move_line.debit
                obj_account_move_line.write(rec_account_move_line.id, {'bank_payment_id': bank_payment_id})

            obj_bank_payment.write(bank_payment_id, {'value': value_total})

        else:

            for line_id in self._context['active_ids']:

                line = obj_account_move_line.browse(line_id)

                if not line.payment_mode_id:
                    continue

                if line.payment_mode_id.generate_bank_payment != True:
                    continue

                if line.bank_payment_id:
                    raise UserError(_('Error! Exist installment(s), related already with a bank payment(s), please cancel the bank payment(s), to can generate new(s) bank payment(s)!'))
                vals = {
                    'name': self.env['ir.sequence'].next_by_code('bank_payment_code_sequence') or _('New'),
                    'date_maturity': line.date_maturity,
                    'date_create': date.today(),
                    'payment_mode_id': line.payment_mode_id.id,
                    'partner_id': line.partner_id.id,
                    'company_id': line.company_id.id,
                    'value': line.debit,
                    'status': 'open'
                }

                if line.payment_mode_id.type_banking_billing == 'REG':
                    vals.update({'our_number': self.env['ir.sequence'].next_by_code(self.our_number_choose(line.payment_mode_id.bank_account_id.bank_id.bic))})

                bank_payment_id = obj_bank_payment.create(vals)

                line.write({'bank_payment_id': bank_payment_id.id})

        return {'type': 'ir.actions.act_window_close'}

    join_installment = fields.Boolean(string='Join Installments', default=False, readonly=True)

