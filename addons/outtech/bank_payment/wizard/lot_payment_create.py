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

class LotPaymentCreate(models.Model):
    _name = 'lot.payment.create'

    def _validate_lines(self):

        first_line = False

        for rec_account_move_line in self.ids:

            if not first_line:

                vals = {
                    'payment_type': rec_account_move_line.payment_type.id,
                    'company_id': rec_account_move_line.company_id.id,
                    'invoice_id': rec_account_move_line.invoice.id
                    }

                first_line = True

            else:
                if rec_account_move_line.payment_type.id != vals['payment_type']:
                    return False, False
                if rec_account_move_line.company_id.id != vals['company_id']:
                    return False, False


        return True

    def create_lot_payment(self):

        lot_payment_id = ''
        amount_total = 0

        obj_lot_payment = self.env['lot.payment']
        obj_account_move_line = self.env['account.move.line']

        for line_id in self._context['active_ids']:

            line = obj_account_move_line.browse(line_id)

            if not line.payment_mode_id:
                continue

            if line.payment_mode_id.generate_lot_payment != True:
                continue

            if line.lot_payment_id:
                raise UserError(_('Error! Exist installment(s), related already with a lot of payment(s), please cancel the lot of payment(s), to can generate new(s) lot of payment(s)!'))

            if not lot_payment_id:
                vals = {
                    'name': self.env['ir.sequence'].next_by_code('lot_payment_code_sequence') or _('New'),
                    'date_create': date.today(),
                    'payment_mode_id': line.payment_mode_id.id,
                    'company_id': line.company_id.id,
                    'status': 'open'
                }

                lot_payment_id = obj_lot_payment.create(vals)

            amount_total += line.credit

            line.write({'lot_payment_id': lot_payment_id.id})

        if lot_payment_id:

            lot_payment_id.write({'value': amount_total})

        return {'type': 'ir.actions.act_window_close'}
