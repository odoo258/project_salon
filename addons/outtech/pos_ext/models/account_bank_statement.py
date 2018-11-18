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

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
from datetime import date

class AccountBankStatement(models.Model):
    _inherit = "account.bank.statement"

    amount_declared = fields.Float('Amount Declared')
    value_difference_box = fields.Float('Box with Difference')

class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    @api.model
    def _get_state_pos(self):

        if self.pos_statement_id:

            self.state_pos = self.pos_statement_id.state

    number_card = fields.Char(string='Number Card')
    flag_card = fields.Char(string='Flag Card')
    number_installments = fields.Integer(string='Number of Installments')
    authorization_number = fields.Char(string="Authorization Number")
    return_tef_reduced = fields.Text(string="Return TEF Reduced")
    return_tef_client = fields.Text(string="Return TEF Client")
    return_tef_cancel = fields.Text(string="Return TEF Client")
    return_tef_establishment = fields.Text(string="Return TEF Establishment")
    type_collection = fields.Selection([('debit', 'Debit'), ('credit', 'Credit'), ('credit_installment', 'Credit Installment')], string='Type of Collection')
    state_pos = fields.Selection(related='pos_statement_id.state', string="State POS")

    def _prepare_reconciliation_move(self, move_ref):

        result = super(AccountBankStatementLine, self)._prepare_reconciliation_move(move_ref)

        result.update({'return_tef': self.return_tef_reduced,
                       'authorization_number': self.authorization_number,
                       'journal_id': self.journal_id.id
                       })

        return result

    def process_reconciliation(self, counterpart_aml_dicts=None, payment_aml_rec=None, new_aml_dicts=None):
        """ Match statement lines with existing payments (eg. checks) and/or payables/receivables (eg. invoices and refunds) and/or new move lines (eg. write-offs).
            If any new journal item needs to be created (via new_aml_dicts or counterpart_aml_dicts), a new journal entry will be created and will contain those
            items, as well as a journal item for the bank statement line.
            Finally, mark the statement line as reconciled by putting the matched moves ids in the column journal_entry_ids.

            :param self: browse collection of records that are supposed to have no accounting entries already linked.
            :param (list of dicts) counterpart_aml_dicts: move lines to create to reconcile with existing payables/receivables.
                The expected keys are :
                - 'name'
                - 'debit'
                - 'credit'
                - 'move_line'
                    # The move line to reconcile (partially if specified debit/credit is lower than move line's credit/debit)

            :param (list of recordsets) payment_aml_rec: recordset move lines representing existing payments (which are already fully reconciled)

            :param (list of dicts) new_aml_dicts: move lines to create. The expected keys are :
                - 'name'
                - 'debit'
                - 'credit'
                - 'account_id'
                - (optional) 'tax_ids'
                - (optional) Other account.move.line fields like analytic_account_id or analytics_id

            :returns: The journal entries with which the transaction was matched. If there was at least an entry in counterpart_aml_dicts or new_aml_dicts, this list contains
                the move created by the reconciliation, containing entries for the statement.line (1), the counterpart move lines (0..*) and the new move lines (0..*).
        """
        counterpart_aml_dicts = counterpart_aml_dicts or []
        payment_aml_rec = payment_aml_rec or self.env['account.move.line']
        new_aml_dicts = new_aml_dicts or []

        aml_obj = self.env['account.move.line']

        company_currency = self.journal_id.company_id.currency_id
        statement_currency = self.journal_id.currency_id or company_currency
        st_line_currency = self.currency_id or statement_currency

        counterpart_moves = self.env['account.move']

        # Check and prepare received data
        if any(rec.statement_id for rec in payment_aml_rec):
            raise UserError(_('A selected move line was already reconciled.'))
        for aml_dict in counterpart_aml_dicts:
            if aml_dict['move_line'].reconciled:
                raise UserError(_('A selected move line was already reconciled.'))
            if isinstance(aml_dict['move_line'], (int, long)):
                aml_dict['move_line'] = aml_obj.browse(aml_dict['move_line'])
        for aml_dict in (counterpart_aml_dicts + new_aml_dicts):
            if aml_dict.get('tax_ids') and aml_dict['tax_ids'] and isinstance(aml_dict['tax_ids'][0], (int, long)):
                # Transform the value in the format required for One2many and Many2many fields
                aml_dict['tax_ids'] = map(lambda id: (4, id, None), aml_dict['tax_ids'])

        # Fully reconciled moves are just linked to the bank statement
        total = self.amount
        for aml_rec in payment_aml_rec:
            total -= aml_rec.debit - aml_rec.credit
            aml_rec.write({'statement_id': self.statement_id.id})
            aml_rec.move_id.write({'statement_line_id': self.id})
            counterpart_moves = (counterpart_moves | aml_rec.move_id)

        # Create move line(s). Either matching an existing journal entry (eg. invoice), in which
        # case we reconcile the existing and the new move lines together, or being a write-off.
        if counterpart_aml_dicts or new_aml_dicts:
            st_line_currency = self.currency_id or statement_currency
            st_line_currency_rate = self.currency_id and (self.amount_currency / self.amount) or False

            # Create the move
            self.sequence = self.statement_id.line_ids.ids.index(self.id) + 1
            move_vals = self._prepare_reconciliation_move(self.statement_id.name)
            move = self.env['account.move'].create(move_vals)
            counterpart_moves = (counterpart_moves | move)

            # Create The payment
            payment = False
            if abs(total) > 0.00001:
                partner_id = self.partner_id and self.partner_id.id or False
                partner_type = False
                if partner_id:
                    if total < 0:
                        partner_type = 'supplier'
                    else:
                        partner_type = 'customer'

                payment_methods = (
                                  total > 0) and self.journal_id.inbound_payment_method_ids or self.journal_id.outbound_payment_method_ids
                currency = self.journal_id.currency_id or self.company_id.currency_id
                payment = self.env['account.payment'].create({
                    'payment_method_id': payment_methods and payment_methods[0].id or False,
                    'payment_type': total > 0 and 'inbound' or 'outbound',
                    'partner_id': self.partner_id and self.partner_id.id or False,
                    'partner_type': partner_type,
                    'journal_id': self.statement_id.journal_id.id,
                    'payment_date': self.date,
                    'state': 'reconciled',
                    'currency_id': currency.id,
                    'amount': abs(total),
                    'communication': self.name or '',
                    'name': self.statement_id.name,
                })

            # Complete dicts to create both counterpart move lines and write-offs
            to_create = (counterpart_aml_dicts + new_aml_dicts)
            ctx = dict(self._context, date=self.date)
            for aml_dict in to_create:

                range_days_maturity_date = 0

                if self.type_collection == 'debit':
                    range_days_maturity_date = self.journal_id.range_days_maturity_date_debit
                elif self.type_collection == 'credit':
                    range_days_maturity_date = self.journal_id.range_days_maturity_date_credit

                aml_dict['date_maturity'] = date.fromordinal(date.today().toordinal() + range_days_maturity_date)

                aml_dict['payment_mode_id'] = self.statement_id.journal_id.payment_mode_id and self.statement_id.journal_id.payment_mode_id.id or ''
                aml_dict['move_id'] = move.id
                aml_dict['partner_id'] = self.partner_id.id
                aml_dict['statement_id'] = self.statement_id.id
                if st_line_currency.id != company_currency.id:
                    aml_dict['amount_currency'] = aml_dict['debit'] - aml_dict['credit']
                    aml_dict['currency_id'] = st_line_currency.id
                    if self.currency_id and statement_currency.id == company_currency.id and st_line_currency_rate:
                        # Statement is in company currency but the transaction is in foreign currency
                        aml_dict['debit'] = company_currency.round(aml_dict['debit'] / st_line_currency_rate)
                        aml_dict['credit'] = company_currency.round(aml_dict['credit'] / st_line_currency_rate)
                    elif self.currency_id and st_line_currency_rate:
                        # Statement is in foreign currency and the transaction is in another one
                        aml_dict['debit'] = statement_currency.with_context(ctx).compute(
                            aml_dict['debit'] / st_line_currency_rate, company_currency)
                        aml_dict['credit'] = statement_currency.with_context(ctx).compute(
                            aml_dict['credit'] / st_line_currency_rate, company_currency)
                    else:
                        # Statement is in foreign currency and no extra currency is given for the transaction
                        aml_dict['debit'] = st_line_currency.with_context(ctx).compute(aml_dict['debit'],
                                                                                       company_currency)
                        aml_dict['credit'] = st_line_currency.with_context(ctx).compute(aml_dict['credit'],
                                                                                        company_currency)
                elif statement_currency.id != company_currency.id:
                    # Statement is in foreign currency but the transaction is in company currency
                    prorata_factor = (aml_dict['debit'] - aml_dict['credit']) / self.amount_currency
                    aml_dict['amount_currency'] = prorata_factor * self.amount
                    aml_dict['currency_id'] = statement_currency.id

            # Create write-offs
            # When we register a payment on an invoice, the write-off line contains the amount
            # currency if all related invoices have the same currency. We apply the same logic in
            # the manual reconciliation.
            counterpart_aml = self.env['account.move.line']
            for aml_dict in counterpart_aml_dicts:
                counterpart_aml |= aml_dict.get('move_line', self.env['account.move.line'])
            new_aml_currency = False
            if counterpart_aml \
                    and len(counterpart_aml.mapped('currency_id')) == 1 \
                    and counterpart_aml[0].currency_id \
                    and counterpart_aml[0].currency_id != company_currency:
                new_aml_currency = counterpart_aml[0].currency_id
            for aml_dict in new_aml_dicts:
                aml_dict['payment_id'] = payment and payment.id or False
                if new_aml_currency and not aml_dict.get('currency_id'):
                    aml_dict['currency_id'] = new_aml_currency.id
                    aml_dict['amount_currency'] = company_currency.with_context(ctx).compute(
                        aml_dict['debit'] - aml_dict['credit'], new_aml_currency)
                aml_obj.with_context(check_move_validity=False, apply_taxes=True).create(aml_dict)

            # Create counterpart move lines and reconcile them
            for aml_dict in counterpart_aml_dicts:
                if aml_dict['move_line'].partner_id.id:
                    aml_dict['partner_id'] = aml_dict['move_line'].partner_id.id
                aml_dict['account_id'] = aml_dict['move_line'].account_id.id
                aml_dict['payment_id'] = payment and payment.id or False

                counterpart_move_line = aml_dict.pop('move_line')
                if counterpart_move_line.currency_id and counterpart_move_line.currency_id != company_currency and not aml_dict.get(
                        'currency_id'):
                    aml_dict['currency_id'] = counterpart_move_line.currency_id.id
                    aml_dict['amount_currency'] = company_currency.with_context(ctx).compute(
                        aml_dict['debit'] - aml_dict['credit'], counterpart_move_line.currency_id)
                new_aml = aml_obj.with_context(check_move_validity=False).create(aml_dict)

                (new_aml | counterpart_move_line).reconcile()

            # Create the move line for the statement line using the bank statement line as the remaining amount
            # This leaves out the amount already reconciled and avoids rounding errors from currency conversion
            st_line_amount = -sum([x.balance for x in move.line_ids])
            aml_dict = self._prepare_reconciliation_move_line(move, st_line_amount)
            aml_dict['payment_mode_id'] = self.statement_id.journal_id.payment_mode_id and self.statement_id.journal_id.payment_mode_id.id or ''

            range_days_maturity_date = 0

            if self.type_collection == 'debit':
                range_days_maturity_date = self.journal_id.range_days_maturity_date_debit
            elif self.type_collection == 'credit':
                range_days_maturity_date = self.journal_id.range_days_maturity_date_credit

            aml_dict['date_maturity'] = date.fromordinal(date.today().toordinal() + range_days_maturity_date)
            aml_dict['payment_id'] = payment and payment.id or False
            if self.journal_id.is_tef:
                aml_dict['account_id'] = self.journal_id.default_debit_account_id.id
            aml_obj.with_context(check_move_validity=False).create(aml_dict)

            if self.number_installments > 1 and (self.statement_id.journal_id.is_tef or self.statement_id.journal_id.is_contingency):

                for move_line in move.line_ids:

                    if self.journal_id.default_debit_account_id.id == move_line.account_id.id:

                        amount = (st_line_amount / self.number_installments)
                        amount = round(amount, self.env['decimal.precision'].precision_get('Account'))

                        total_installment = self.number_installments < 10 and "0%s" % str(self.number_installments) or str(self.number_installments)

                        move_line.write({'name': "%s (01/%s)" % (self.name, total_installment),
                                         'credit': amount < 0 and -amount or 0.0,
                                         'debit': amount > 0 and amount or 0.0,
                                         'date_maturity': date.fromordinal(date.today().toordinal()+move_line.statement_id.journal_id.range_days_maturity_date_credit_instalments)})
                        i = 2

                        while i <= self.number_installments:

                            if i == self.number_installments:

                                amount_total = amount * self.number_installments

                                if amount_total < st_line_amount:

                                    amount = amount + (st_line_amount - amount_total)

                                if amount_total > st_line_amount:

                                    amount = amount - (amount_total - st_line_amount)

                            installment_current = i < 10 and "0%s" % str(i) or str(i)

                            vals = {
                                'name': "%s (%s/%s)" % (self.name, installment_current, total_installment),
                                'move_id': move.id,
                                'partner_id': self.partner_id and self.partner_id.id or False,
                                'account_id': amount >= 0 and self.journal_id.default_credit_account_id.id or self.journal_id.default_debit_account_id.id,
                                'credit': amount < 0 and -amount or 0.0,
                                'debit': amount > 0 and amount or 0.0,
                                'statement_id': self.statement_id.id,
                                'currency_id': move_line.currency_id.id,
                                'amount_currency': 0,
                                'date_maturity': date.fromordinal(date.today().toordinal() + (move_line.statement_id.journal_id.range_days_maturity_date_credit_instalments * i))
                            }

                            vals['payment_id'] = payment and payment.id or False

                            move_line.create(vals)

                            i += 1



            move.post()
            # record the move name on the statement line to be able to retrieve it in case of unreconciliation
            self.write({'move_name': move.name})
            payment.write({'payment_reference': move.name})
        elif self.move_name:
            raise UserError(_(
                'Operation not allowed. Since your statement line already received a number, you cannot reconcile it entirely with existing journal entries otherwise it would make a gap in the numbering. You should book an entry and make a regular revert of it in case you want to cancel it.'))
        counterpart_moves.assert_balanced()
        return counterpart_moves
