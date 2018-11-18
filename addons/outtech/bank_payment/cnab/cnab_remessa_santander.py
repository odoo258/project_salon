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

from decimal import Decimal, Context, Inexact
from datetime import datetime, date
from itertools import count
import base64
import pytz
import re

def counter(start=0):
    try:
        return count(start=start)
    except TypeError:
        c = count()
        c.next()
        return c

if hasattr(Decimal, 'from_float'):
    float_to_decimal = Decimal.from_float
else:
    def float_to_decimal(f):
        "Convert a floating point number to a Decimal with no loss of information"
        n, d = f.as_integer_ratio()
        numerator, denominator = Decimal(n), Decimal(d)
        ctx = Context(prec=60)
        result = ctx.divide(numerator, denominator)
        while ctx.flags[Inexact]:
            ctx.flags[Inexact] = False
            ctx.prec *= 2
            result = ctx.divide(numerator, denominator)
        return result

class CnabRemessaSantander(models.Model):
    _name = 'cnab.remessa.santander'

    def _round(self, v):
        v = float_to_decimal(v)
        return (v * Decimal('100')).quantize(1)

    def _only_digits(self, v):

        if v == False:
            return v == ''
        else:
            return re.sub('[^0-9]', '', str(v))

    def _spe_char_remove(self, text):

        if text == None or text == False:
            return text == ''

        text = (text).encode('utf-8')

        dic = {'á':'a', 'à':'a', 'â':'a', 'ã':'a', 'Á':'A', 'À':'A', 'Â':'A', 'Ã':'A',
               'é':'e', 'è':'e', 'ê':'e', 'ẽ':'e', 'É':'E', 'È':'E', 'Ê':'E', 'Ẽ':'E',
               'í':'i', 'ì':'i', 'î':'i', 'ĩ':'i', 'Í':'I', 'Ì':'I', 'Î':'I', 'Ĩ':'I',
               'ó':'o', 'ò':'o', 'ô':'o', 'õ':'o', 'Ó':'O', 'Ò':'O', 'Ô':'O', 'Õ':'O',
               'ú':'u', 'ù':'u', 'û':'u', 'ũ':'u', 'Ú':'U', 'Ù':'U', 'Û':'U', 'Ũ':'U',
               'ç':'c', 'Ç':'C'}

        for s, r in dic.iteritems():
            text = text.replace(s, r)

        return re.sub('[^a-zA-Z0-9/&. -]', '', text)

    def _get_address(self, partner, len_adress):

        if partner.street2:
            w_address = '%s, %s, %s ' % ((partner.street or ''),(partner.number or ''),(partner.street2 or ''))

        else:
            w_address = '%s, %s' % ((partner.street or ''),(partner.number or ''))

        if len(w_address) > len_adress:

            difference = len(w_address) - len_adress
            w_street = partner.street
            w_street = w_street.encode('latin-1')
            w_street = w_street[:len(w_street)-difference]
            w_street = w_street.decode('unicode-escape')

            if partner.street2:
                w_address = '%s, %s, %s ' % ((w_street or ''), (partner.number or ''), partner.street2)
            else:
                w_address = '%s, %s' % ((w_street or ''), (partner.number or ''))

        return self._spe_char_remove(w_address)

    def get_complement(self, bank_account, dig_bank_account):

        num_bank_account = len(bank_account)
        last_dig_bank_account = bank_account[num_bank_account - 1]

        complement = '%s%s' % (last_dig_bank_account, dig_bank_account)

        return complement

    def header(self, rec_payment_mode, numero_sequencial_registro):

        return {
                # 'CodigoRegistro': '0',
                # 'CodigoRemessa': 1,
                # 'LiteralTransmissao': REMESSA,
                # 'CodigoServico': 01,
                # 'LiteralServico': COBRANÇA,
                'CodigoTransmissao': rec_payment_mode.transmission_code,
                'NomeCedente': rec_payment_mode.company_id.name,
                # 'CodigoBanco': '033',
                # 'NomeBanco': 'SANTANDER'
                'DataGravacaoArquivo': date.today(),
                # 'Zeros': '0(16)'
                # 'Brancos': '(275)',
                # 'NumeroVersao': '000', #optional
                'NumeroSequencialRegistro': numero_sequencial_registro
               }

    def detalhe(self, rec_bank_payment, numero_sequencial_registro):

        if rec_bank_payment.payment_mode_id.type_banking_billing == 'REG':
            our_number = rec_bank_payment.our_number

        elif rec_bank_payment.payment_mode_id.type_banking_billing == 'ESC':
            our_number = 00000000

        interest = rec_bank_payment.payment_mode_id.late_payment_interest
        monthly_fine = (rec_bank_payment.value/100)
        monthly_fine = (monthly_fine*interest)
        monthly_fine = round(monthly_fine, 5)
        monthly_fine = str(monthly_fine)

        daily_fine = rec_bank_payment.payment_mode_id.late_payment_fee

        value_daily_fine = 0.00

        if daily_fine:
            value_daily_fine = rec_bank_payment.value * (daily_fine/100)
            value_daily_fine = ("%.2f" % value_daily_fine)

        perc_monthly_fine = rec_bank_payment.payment_mode_id.late_payment_fee
        if perc_monthly_fine:
            perc_monthly_fine = ("%.2f" % perc_monthly_fine)
            perc_monthly_fine = self._only_digits(perc_monthly_fine)

        if rec_bank_payment.partner_id.is_company == True:
            partner_cnpj_cpf = '02'
        else:
            partner_cnpj_cpf = '01'

        return {rec_bank_payment.name:{

                # 'CodigoRegistro': '1',
                # 'TipoInscricaoEmpresa': '02',
                'NumeroInscricaoEmpresa': rec_bank_payment.payment_mode_id.company_id.partner_id.cnpj_cpf,
                'CodigoAgenciaBeneficiario': rec_bank_payment.payment_mode_id.bank_account_id.bra_number or '0000',
                'ContaMovimentoBeneficiario': '07528264',
                'ContaCobrancaBeneficiario': rec_bank_payment.payment_mode_id.bank_account_id.acc_number or '00000000',
                'UsoEmpresa': '',
                'NossoNumero': our_number,
                'DataLimiteDesconto': '',
                # 'Brancos': '(1)',
                'Multa': perc_monthly_fine and 4 or 0,
                'PercentualMulta': perc_monthly_fine,
                # 'Moeda': 00,
                'ValorTitulo': rec_bank_payment.value,
                # 'Brancos': '(4)',
                # 'DataCobrancaMulta': '',
                'CodigoCarteira': rec_bank_payment.payment_mode_id.boleto_carteira,
                # 'IdentificacaoOcorrencia': '01',
                'NumeroDocumento':rec_bank_payment.name,
                'DataVencimentoTitulo': datetime.strptime(rec_bank_payment.date_maturity, '%Y-%m-%d'),
                'ValorTitulo': rec_bank_payment.value,
                # 'NumeroBanco': '033',
                'CodigoAgenciaCobradora': '',
                'EspecieTitulo': str(rec_bank_payment.payment_mode_id.boleto_especie),
                'Aceite': str(rec_bank_payment.payment_mode_id.boleto_aceite),
                'DataEmissaoTitulo': datetime.strptime(rec_bank_payment.date_create, '%Y-%m-%d'),
                '1Instrucao': '',
                '2Instrucao': '',
                'MoraDiaria': value_daily_fine or 0.0,
                'DataLimiteDesconto': '',
                'ValorDesconto': 0.0,
                'ValorIOF': 0.0,
                'ValorAbatimento': 0.0,
                'IdentificacaoInscricaoSacado': partner_cnpj_cpf,
                'NumeroInscricaoSacado': self._only_digits(rec_bank_payment.partner_id.cnpj_cpf),
                'NomeSacado': self._spe_char_remove(rec_bank_payment.partner_id.name),
                'EnderecoCompleto40': self._get_address(rec_bank_payment.partner_id, 40),
                'Bairro': rec_bank_payment.partner_id.district,
                'Cep':rec_bank_payment.partner_id.zip,
                'Cidade': rec_bank_payment.partner_id.city_id.name,
                'Estado': (rec_bank_payment.partner_id.state_id and rec_bank_payment.partner_id.state_id.code or ''),
                'SacadorAvalista': '',
                # 'Brancos': '(1)',
                # 'IdentificadorComplemento': 'I',
                'ComplementoConta': self.get_complement(rec_bank_payment.payment_mode_id.bank_account_id.acc_number, rec_bank_payment.payment_mode_id.bank_account_id.acc_number_dig),
                # 'Brancos': '(6)',
                'DiasProtesto': '',
                # 'Brancos': '(1)',
                'NumeroSequencialRegistro': numero_sequencial_registro
                }}

    def trailer(self, numero_sequencial_registro, total_value_title_bank):


        return {
                # 'IdentificacaoRegistro': '9',
                'QuantidadeTitulos': numero_sequencial_registro - 2,
                'ValorTotal': total_value_title_bank,
                # 'Zeros': 0(374),
                'NumeroSequencialRegistro': numero_sequencial_registro
                }


    def gerar_cnab_remessa_santander(self, bank_title_santander):

        numero_sequencial_registro = 1

        total_value_title_bank = 0
        file_remessa = []

        dict_data = {'header': {}, 'detail': {}, 'footer': {}}

        dict_data['header'].update(self.header(bank_title_santander[0].payment_mode_id, numero_sequencial_registro))

        numero_sequencial_registro += 1

        for rec_bank_payment in bank_title_santander:
            dict_data['detail'].update(self.detalhe(rec_bank_payment, numero_sequencial_registro))

            numero_sequencial_registro += 1
            total_value_title_bank += rec_bank_payment.value

        dict_data['footer'].update(self.trailer(numero_sequencial_registro, total_value_title_bank))

        result = self.env['file.export.layout'].create_file('RemessaBancariaSantander', dict_data)

        # Convert Hours
        w_timezone = self.env['res.users'].browse(self._uid).tz
        now = datetime.now(pytz.timezone(w_timezone))
        now_utc = datetime.today()

        filename = 'REM_%s_%04d%02d%02d_%02d%02d%02d.REM' % (rec_bank_payment.payment_mode_id.bank_account_id.bank_id.bic,
                                                             now.year,
                                                             now.month,
                                                             now.day,
                                                             now.hour,
                                                             now.minute,
                                                             now.second)

        encoded_result = base64.b64encode(result)

        self.env['bank.file'].create({'cnab_file': encoded_result, 'filename': filename, 'file_type': 'remessa_cnab', 'date_time': now_utc, 'bank_id': rec_bank_payment.payment_mode_id.bank_account_id.bank_id.id})
