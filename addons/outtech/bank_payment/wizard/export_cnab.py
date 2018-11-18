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

class CnabExport(models.Model):
    _name = 'cnab.export'

    def generate_bank_remessa(self):

        bank_title_itau = []
        bank_title_bradesco = []
        bank_title_santander = []
        bank_title_bbrasil = []
        bank_title_siccob = []

        for rec_bank_payment in self.env['bank.payment'].browse(self._context['active_ids']):

            if rec_bank_payment.status in ('paid', 'canceled'):
                continue

            msg = self.validate(rec_bank_payment)
            if msg:
                raise UserError(_('Error: %s') %msg)

            bank_code = rec_bank_payment.payment_mode_id.bank_account_id.bank_id.bic

            if bank_code == '033':  # Santander
                bank_title_santander.append(rec_bank_payment)

            # elif bank_code == '237': # Bradesco
            #     bank_title_bradesco.append(rec_bank_payment)
            #
            # elif bank_code == '341':   # Itau
            #     bank_title_itau.append(rec_bank_payment)
            #
            #
            # elif bank_code == '001': # Banco do Brasil
            #     bank_title_bbrasil.append(rec_bank_payment)
            #
            # elif bank_code == '756': # Siccob
            #     bank_title_siccob.append(rec_bank_payment)

            else:
                continue

        # if bank_title_itau:   # Itau
        #     self.pool.get('cnab.remessa.itau').gerar_cnab_remessa_itau(bank_title_itau)
        #
        # if bank_title_bradesco: # Bradesco
        #     self.pool.get('cnab.remessa.bradesco').gerar_cnab_remessa_bradesco(bank_title_bradesco)

        if bank_title_santander: # Santander
            self.env['cnab.remessa.santander'].gerar_cnab_remessa_santander(bank_title_santander)

        # if bank_title_bbrasil: # Banco do Brasil
        #     self.pool.get('cnab.remessa.bbrasil').gerar_cnab_remessa_bbrasil(bank_title_bbrasil)
        #
        # if bank_title_siccob: # Siccob
        #     self.pool.get('cnab.remessa.sicoob').gerar_cnab_remessa_sicoob(bank_title_siccob)

        return {'type': 'ir.actions.act_window_close'}

    def validate(self, rec_bank_payment):

        if not rec_bank_payment.payment_mode_id.bank_account_id:
            return ('%s - %s') %(rec_bank_payment.name, u'Bank account is not defined in payment type')

        if not rec_bank_payment.payment_mode_id.type_banking_billing:
            return ('%s - %s') %(rec_bank_payment.name, u'Bank collection type not defined')

        if rec_bank_payment.payment_mode_id.type_banking_billing == 'REG' and rec_bank_payment.our_number == False:
            return ('%s - %s') %(rec_bank_payment.name, u'Bank title does not have "our_number" defined, please firstly generate the bank payment slip to get the "our_number".')

        if rec_bank_payment.payment_mode_id.type_banking_billing == 'SRG':
            return ('%s - %s') %(rec_bank_payment.name, u'Your bank collection type is "Sem Registro", you can not generate the remessa file')

        if not rec_bank_payment.payment_mode_id.layout_remessa:
            return ('%s - %s') %(rec_bank_payment.name, u'Do not have Remessa layout config in the payment type')

        return ''

    def generate_open_bank_file(self):

        self.generate_bank_remessa()

        ir_model_data = self.env['ir.model.data']
        tree_res = ir_model_data.get_object_reference('bank_payment', 'bank_file_tree')
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