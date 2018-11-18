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
from odoo import models, api, _, fields

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    payment_installment = fields.Boolean(string="Installment Payment")
    payment_difference_handling_installment = fields.Selection([('open', 'Keep open'), ('reconcile', 'Mark installment as fully paid')], default='open', string="Payment Difference", copy=False)

    def _create_payment_entry(self, amount):
        """ Create a journal entry corresponding to a payment, if the payment references invoice(s) they are reconciled.
            Return the journal entry.
        """
        self = self.with_context(move_line_to_reconcile=self.move_line_id)
        if not self.invoice_ids:
            self.invoice_ids = self.move_line_id.invoice_id
        aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
        invoice_currency = False
        if self.invoice_ids and all([x.currency_id == self.invoice_ids[0].currency_id for x in self.invoice_ids]):
            #if all the invoices selected share the same currency, record the paiement in that currency too
            invoice_currency = self.invoice_ids[0].currency_id
        debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date).compute_amount_fields(amount, self.currency_id, self.company_id.currency_id, invoice_currency)

        move = self.env['account.move'].create(self._get_move_vals())

        #Write line corresponding to invoice payment
        counterpart_aml_dict = self._get_shared_move_line_vals(debit, credit, amount_currency, move.id, False)
        counterpart_aml_dict.update(self._get_counterpart_move_line_vals(self.invoice_ids))
        counterpart_aml_dict.update({'currency_id': currency_id})
        counterpart_aml = aml_obj.create(counterpart_aml_dict)

        #Reconcile with the invoices
        if self.payment_difference_handling == 'reconcile' or self.payment_difference_handling_installment == 'reconcile' and self.payment_difference:
            writeoff_line = self._get_shared_move_line_vals(0, 0, 0, move.id, False)
            debit_wo, credit_wo, amount_currency_wo, currency_id = aml_obj.with_context(date=self.payment_date).compute_amount_fields(self.payment_difference, self.currency_id, self.company_id.currency_id, invoice_currency)
            writeoff_line['name'] = _('Counterpart')
            writeoff_line['account_id'] = self.writeoff_account_id.id
            writeoff_line['debit'] = debit_wo
            writeoff_line['credit'] = credit_wo
            writeoff_line['amount_currency'] = amount_currency_wo
            writeoff_line['currency_id'] = currency_id
            writeoff_line = aml_obj.create(writeoff_line)
            if counterpart_aml['debit']:
                counterpart_aml['debit'] += credit_wo - debit_wo
            if counterpart_aml['credit']:
                counterpart_aml['credit'] += debit_wo - credit_wo
            counterpart_aml['amount_currency'] -= amount_currency_wo
        self.invoice_ids.register_payment(counterpart_aml)

        #Write counterpart lines
        if not self.currency_id != self.company_id.currency_id:
            amount_currency = 0
        liquidity_aml_dict = self._get_shared_move_line_vals(credit, debit, -amount_currency, move.id, False)
        liquidity_aml_dict.update(self._get_liquidity_move_line_vals(-amount))
        aml_obj.create(liquidity_aml_dict)

        move.post()
        return move

    @api.one
    @api.depends('invoice_ids', 'amount', 'payment_date', 'currency_id')
    def _compute_payment_difference(self):
        amount_paid = 0
        self.payment_installment = False
        if len(self.invoice_ids) == 0 and not self.move_line_id.invoice_id and self.payment_type != 'outbound':
            if self.payment_type == 'outbound':
                if self.move_line_id.matched_credit_ids:
                    for line in self.move_line_id.matched_credit_ids:
                        amount_paid += line.amount
                else:
                    for line in self.move_line_id.matched_debit_ids:
                        amount_paid += line.amount
                self.payment_difference = amount_paid - (self.amount - self.move_line_id.credit)
            else:
                if self.move_line_id.matched_credit_ids:
                    for line in self.move_line_id.matched_credit_ids:
                        amount_paid += line.amount
                else:
                    for line in self.move_line_id.matched_debit_ids:
                        amount_paid += line.amount
                self.payment_difference = (self.move_line_id.debit - self.amount) - amount_paid
            return
        src_move_installments = self.env['account.move.line'].search(
            [('move_id', '=', self.move_line_id.move_id.id), ('debit', '>', 0)])
        if src_move_installments:
            if self.move_line_id.id in src_move_installments.ids:
                self.payment_installment = True
                if self.amount != self.move_line_id.amount_residual:
                    self.payment_difference = self.move_line_id.amount_residual - self.amount
                    return True
                else:
                    return True
            else:
                src_move_installments = self.env['account.move.line'].search(
                    [('move_id', '=', self.move_line_id.move_id.id), ('credit', '>', 0)])
                if src_move_installments:
                    if self.move_line_id.id in src_move_installments.ids:
                        self.payment_installment = True
                        if self.amount != self.move_line_id.amount_residual:
                            self.payment_difference = self.move_line_id.amount_residual + self.amount
                            return True
                        else:
                            return True
        if self.move_line_id.invoice_id and not self.invoice_ids:
            invoice_id = self.move_line_id.invoice_id
            if invoice_id.type in ['in_invoice', 'out_refund']:
                self.payment_difference = self.amount - invoice_id.residual_signed
                return True
            else:
                self.payment_difference = invoice_id.residual_signed - self.amount
                return True
        if self.invoice_ids:
            if self.invoice_ids[0].type in ['in_invoice', 'out_refund']:
                self.payment_difference = self.amount - self._compute_total_invoices_amount()
            elif self.invoice_ids:
                self.payment_difference = self._compute_total_invoices_amount() - self.amount
        else:
            if self.payment_type == 'outbound':
                if self.move_line_id.matched_credit_ids:
                    for line in self.move_line_id.matched_credit_ids:
                        amount_paid += line.amount
                else:
                    for line in self.move_line_id.matched_debit_ids:
                        amount_paid += line.amount
                self.payment_difference = amount_paid - (self.amount - self.move_line_id.credit)
            else:
                if self.move_line_id.matched_credit_ids:
                    for line in self.move_line_id.matched_credit_ids:
                        amount_paid += line.amount
                else:
                    for line in self.move_line_id.matched_debit_ids:
                        amount_paid += line.amount
                self.payment_difference = (self.move_line_id.debit - self.amount) - amount_paid

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.multi
    def action_register_payment(self):
        dummy, act_id = self.env['ir.model.data'].get_object_reference('account', 'action_account_invoice_payment')
        receivable = (self.user_type_id.type == 'receivable')
        vals = self.env['ir.actions.act_window'].browse(act_id).read()[0]
        amount = self.amount_residual
        if amount != self.balance:
            if amount < 0:
                amount = amount * -1
        else:
            amount = self.debit or self.credit
        vals['context'] = {
            'default_amount': amount,
            'default_partner_type': 'customer' if receivable else 'supplier',
            'default_partner_id': self.partner_id.id,
            'default_communication': self.name,
            'default_payment_type': 'inbound' if receivable else 'outbound',
            'default_move_line_id': self.id, }
        if self.invoice_id:
            vals['context']['default_invoice_ids'] = [(4, self.invoice_id.id, None)],
        return vals