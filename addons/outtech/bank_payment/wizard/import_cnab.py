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
from odoo.exceptions import UserError
from datetime import datetime
from decimal import Decimal

import pytz
import base64

class CnabImport(models.Model):
    _name = 'cnab.import'

    def _cents_to_euros(self, value):
        return float((Decimal(value) / Decimal('100')).quantize(Decimal('1.00')))

    def generate_payment(self, value_paid, payment_date, journal, rec_bank_payment):

        currency = self.env['res.currency'].search([('name', '=', 'BRL')])

        payment_method = self.env['account.payment.method'].search([('code', '=', 'cnab file')])

        communication = ''

        if len(rec_bank_payment.invoice_installment_ids) == 1:
            communication = rec_bank_payment.invoice_installment_ids[0].invoice_id and rec_bank_payment.invoice_installment_ids[0].invoice_id.origin or ''

        if communication == '':
            communication = rec_bank_payment.name


        if not currency:
            raise UserError(_('Error! The currency "BRL" is not registered in currencies. Please register it.'))

        if not payment_method:
            raise UserError(_('Error! The payment method "Cnab File" is not registered in payment methods. Please register it.'))

        installment = 1

        for aml in rec_bank_payment.invoice_installment_ids:

            if value_paid == 0.00:
                continue

            if len(rec_bank_payment.invoice_installment_ids) > 1:

                number_total_installment = len(rec_bank_payment.invoice_installment_ids)

                if value_paid >= aml.debit:
                    value_paid_partial = aml.debit
                    if installment == number_total_installment:
                        value_paid_partial = value_paid
                        payment_difference_handling = 'reconcile'
                        payment_difference = value_paid - aml.debit
                else:
                    value_paid_partial = value_paid

            else:
                if value_paid > aml.debit:
                    value_paid_partial = value_paid
                    payment_difference_handling = 'reconcile'
                    payment_difference = value_paid - aml.debit
                else:
                    value_paid_partial = value_paid
                    payment_difference_handling = 'open'
                    payment_difference = 0.00


            vals = {
                'communication': communication,
                'journal_id': journal.id,
                'currency_id': currency.id,
                'partner_id': rec_bank_payment.partner_id.id,
                'payment_method_id': payment_method.id,
                'payment_date': payment_date,
                'payment_difference': payment_difference,
                'payment_difference_handling': payment_difference_handling,
                'writeoff_account_id': payment_difference_handling == 'reconcile' and rec_bank_payment.payment_mode_id.writeoff_account_id.id or '',
                'company_id': rec_bank_payment.company_id.id,
                'state': 'draft',
                'create_uid': self._uid,
                'partner_type': 'customer',
                'name': 'Draft Payment',
                'amount': value_paid_partial,
                'payment_type': payment_method.payment_type,
                'move_line_id': aml.id
            }

            account_payment = self.env['account.payment'].create(vals)

            account_payment.post()

            value_paid = value_paid - value_paid_partial
            installment += 1

        return True

    def import_file(self):

        obj_bank_payment = self.env['bank.payment']
        obj_bank_file = self.env['bank.file']

        data = base64.b64decode(self.file)

        # Retorno

        if self.type == 'retorno':

            format = self.payment_mode_id.layout_retorno

            if not format:
                raise UserError(_('Error! No layout of retorno registered in payment mode form!'))

            dict_data = self.env['file.import.layout'].import_file('RetornoSantanderCNAB400', data)

            journal = self.payment_mode_id.bank_account_id.journal_id
            if not journal:
                raise UserError(_('Error! Please configure bank journal'))

            for reg in dict_data['detail'][0]:

                line = dict_data['detail'][0][reg]

                date_maturity = '20%s-%s-%s' % (line['DataVencimentoTitulo'][4:], line['DataVencimentoTitulo'][2:-2], line['DataVencimentoTitulo'][:-4])

                if obj_bank_payment.search([('name', '=', line['NumeroDocumento']), ('date_maturity', '=', date_maturity), ('status', '!=', 'paid')]):

                    src_bank_payment = obj_bank_payment.search([('name', '=', line['NumeroDocumento']), ('date_maturity', '=', date_maturity)])

                    if not self.payment_mode_id.bank_account_id.bank_id.code_occurrence_ids:
                        raise UserError(_('Error! Do not exist bank occurrences registered for this bank'))

                    for events in self.payment_mode_id.bank_account_id.bank_id.code_occurrence_ids:

                        if events.code_occurrence == line['IdentificacaoOcorrencia']:

                            if events.action == 'pay':

                                value_paid = self._cents_to_euros(line['ValorPrincipal'])
                                payment_date = '20%s-%s-%s' % (line['DataOcorrencia'][4:], line['DataOcorrencia'][2:-2], line['DataOcorrencia'][:-4])
                                payment_date = datetime.strptime(payment_date, "%Y-%m-%d").date()

                                self.generate_payment(value_paid, payment_date, journal, src_bank_payment)

                                balance = src_bank_payment.value_paid + value_paid

                                if balance >= src_bank_payment.value or ('%.2f' % (src_bank_payment.value - balance) < 0.01):
                                    src_bank_payment.write({'status': 'paid', 'value_paid': balance})
                                else:
                                    src_bank_payment.write({'value_paid': balance})

                            elif events.action == 'confirm':

                                src_bank_payment.write({'status': 'confirmed', 'our_number': line['NossoNumero']})

            w_timezone = self.env['res.users'].browse(self._uid).tz
            now = datetime.now(pytz.timezone(w_timezone))
            now_utc = datetime.today()

            filename = 'RET_%s_%04d%02d%02d_%02d%02d%02d.txt' % (self.payment_mode_id.bank_account_id.bank_id.bic,
                                                                 now.year,
                                                                 now.month,
                                                                 now.day,
                                                                 now.hour,
                                                                 now.minute,
                                                                 now.second)

            obj_bank_file.create({'cnab_file': self.file, 'filename': filename, 'file_type': 'retorno_cnab', 'date_time': now_utc, 'bank_id': self.payment_mode_id.bank_account_id.bank_id.id})

            return self.open_bank_file()

    def open_bank_file(self):

        tree_res = self.env['ir.model.data'].get_object_reference('bank_payment', 'bank_file_tree')
        tree_id = tree_res and tree_res[1] or False

        return {
            'name': _('Consult Bank File'),
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'bank.file',
            'view_id': False,
            'views': [(tree_id, 'tree')],
            'type': 'ir.actions.act_window',
        }

    file = fields.Binary(string='File', required=True)
    type = fields.Selection([('retorno', 'Arquivo de Retorno Bancário')], string='File Type', required=True)
    payment_mode_id = fields.Many2one('payment.mode', string='Payment Mode')
