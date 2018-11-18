# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2018 - OutTech (<http://www.outtech.com.br>).
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
from datetime import datetime, date
from odoo.exceptions import UserError

import base64
import pytz

class PagforRemessaSantander(models.Model):
    _name = 'pagfor.remessa.santander'

    def logical_bar_code(self, bar_code):

        if not bar_code:
            raise UserError(_('Error! Exist installment(s) without barcode number! Please check again!'))

        if not len(bar_code) == 47:
            raise UserError(_('Error! Exist installment(s) with barcode less or greater than 47 characters! Please check again!'))

        try:
            int(bar_code)
        except:
            raise UserError(_('Error! Exist installment(s) with characters not numeric in barcode! Please check again!'))

        bar_code = bar_code[:9] + bar_code[10:]
        bar_code = bar_code[:19] + bar_code[20:]
        bar_code = bar_code[:29] + bar_code[30:]

        return bar_code


    def header(self, rec_payment_mode):

        if rec_payment_mode.company_id.partner_id.is_company == True:
            company_cnpj_cpf = 2
        else:
            company_cnpj_cpf = 1

        hour_now = '%02d%02d%02d' %(datetime.now().hour, datetime.now().minute, datetime.now().second)

        return {
                    # 'CodigoBanco': 033,
                    # 'LoteServico': 0000,
                    # 'TipoRegistro': 0,
                    # 'Brancos': '(9)',
                    'TipoInscricaoEmpresa': company_cnpj_cpf,
                    'NumeroInscricaoEmpresa': rec_payment_mode.company_id.partner_id.cnpj_cpf,
                    'CodigoConvenioBanco': rec_payment_mode.bank_account_id.codigo_convenio or 0,
                    'AgenciaMantenedoraConta': rec_payment_mode.bank_account_id.bra_number or 0,
                    'DigitoVerificadorAgencia': rec_payment_mode.bank_account_id.bra_number_dig or 0,
                    'NumeroContaCorrente': rec_payment_mode.bank_account_id.acc_number or 0,
                    'DigitoVerificadorConta': rec_payment_mode.bank_account_id.acc_number_dig or 0,
                    'DigitoVerificadorAgenciaConta': '',
                    'NomeEmpresa': rec_payment_mode.company_id.name,
                    # 'NomeBanco': 'Banco Santander'
                    # 'Brancos': '(10)',
                    # 'CodigoRemessaRetorno': 1,
                    'DataGeracaoArquivo': date.today(),
                    'HoraGeracaoArquivo': int(hour_now),
                    'NumeroSequencialArquivo': self.env['ir.sequence'].next_by_code('header_file_pagfor_santander') or 0,
                    # 'NumeroVersaoLayout': 060,
                    # 'DensidadeGravacaoArquivo': 00000,
                    'UsoReservadoBanco': '',
                    'UsoReservadoEmpresa': '',
                    # 'Brancos': '(19)',
                    'OcorrenciasRetorno': '',
                }


    def lot_header(self, rec_lot_payment, total_lot_payment):

        if rec_lot_payment.payment_mode_id.company_id.partner_id.is_company == True:
            company_cnpj_cpf = 2
        else:
            company_cnpj_cpf = 1

        return {total_lot_payment:{
                    # 'CodigoBanco': 033,
                    'LoteServico': total_lot_payment,
                    # 'TipoRegistro': 1,
                    # 'TipoOperacao': 'C',
                    # 'TipoServico': 20,
                    # 'FormaLancamento': 11,
                    # 'NumeroVersaoLote': 030 ,
                    # 'Brancos': '(1)',
                    'TipoInscricaoEmpresa': company_cnpj_cpf,
                    'NumeroInscricaoEmpresa': rec_lot_payment.payment_mode_id.company_id.partner_id.cnpj_cpf or 0,
                    'CodigoConvenioBanco': rec_lot_payment.payment_mode_id.bank_account_id.codigo_convenio or 0,
                    'AgenciaMantenedoraConta': rec_lot_payment.payment_mode_id.bank_account_id.bra_number or 0,
                    'DigitoVerificadorAgencia': rec_lot_payment.payment_mode_id.bank_account_id.bra_number_dig or 0,
                    'NumeroContaCorrente': rec_lot_payment.payment_mode_id.bank_account_id.acc_number or 0,
                    'DigitoVerificadorConta': rec_lot_payment.payment_mode_id.bank_account_id.acc_number_dig or 0,
                    'DigitoVerificadorAgenciaConta': '',
                    'NomeEmpresa': rec_lot_payment.payment_mode_id.company_id.name,
                    'Informacao1Mensagem': '',#TODO
                    'Endereco': rec_lot_payment.payment_mode_id.company_id.partner_id.street or '',
                    'Numero': rec_lot_payment.payment_mode_id.company_id.partner_id.number or 0,
                    'ComplementoEndereco': rec_lot_payment.payment_mode_id.company_id.partner_id.street2 or '',
                    'Cidade': rec_lot_payment.payment_mode_id.company_id.partner_id.city_id.name or '',
                    'CEP': rec_lot_payment.payment_mode_id.company_id.partner_id.zip or '',
                    'UF': rec_lot_payment.payment_mode_id.company_id.partner_id.state_id.code or '',
                    # 'Brancos': '(8)',
                    'OcorrenciasRetorno': '',
                }}


    def detalhe(self, rec_lot_payment_line, total_detail_payment, total_lot_payment):

        return {'%s/%s' %(total_lot_payment, total_detail_payment):{
                    # 'CodigoBanco': 033,
                    'LoteServico': total_lot_payment,
                    # 'TipoRegistro': 3,
                    'NumeroSequencialRegistroLote': total_detail_payment,
                    # 'CodigoSegmentoRegistroDetalhe': 'J',
                    # 'TipoMovimento': 0,
                    # 'CodigoInstrucaoMovimento': , #TODO
                    'CodigoBarras': self.logical_bar_code(rec_lot_payment_line.bank_slip_bar_code) or 0,
                    'NomeCedente': rec_lot_payment_line.invoice_id.partner_id.name,
                    'DataVencimento': datetime.strptime(rec_lot_payment_line.date_maturity, '%Y-%m-%d') or 0,
                    'ValorNominalTitulo': rec_lot_payment_line.credit or 0,
                    'ValorDescontoAbatimento': 0,
                    'ValorMultaJuros': 0,
                    'DataPagamento': 0, #TODO
                    'ValorPagamento': 0, #TODO
                    'QuantidadeMoeda': 0,
                    'NumeroDocumentoCliente': self.env['ir.sequence'].next_by_code('detail_file_pagfor_santander') or 0,
                    'NumeroDocumentoBanco': '',
                    'CodigoMoeda': 0, #TODO
                    # 'Brancos': '(6)',
                    'OcorrenciasRetorno': '',
                }}


    def lot_trailer(self, total_lot_payment, total_detail_payment, total_value_supplier_payment):


        return {total_lot_payment:{
                    # 'CodigoBanco': 033,
                    'LoteServico': total_lot_payment,
                    # 'TipoRegistro': 5,
                    # 'Brancos': '(9)',
                    'QuantidadeRegistrosLote': total_detail_payment + 2,
                    'SomatoriaValores': total_value_supplier_payment,
                    'SomatoriaQuantidadeMoedas': 0,
                    'NumeroAvisoDébito': 0,
                    # 'Brancos': '(165)',
                    'OcorrenciasRetorno': '',
                }}


    def trailer(self, total_lot_payment, total_detail_payments):

        return {
                # 'CodigoBanco': 033,
                # 'LoteServico': 9999,
                # 'TipoRegistro': 5,
                # 'Brancos': '(9)',
                'QuantidadeLotesArquivo': total_lot_payment,
                'QuantidadeRegistrosArquivo': (total_detail_payments + (total_lot_payment * 2) + 2),
                # 'Brancos': '(211)',
            }


    def gerar_lot_pagfor_remessa_santander(self, lot_payment_santander):

        total_value_supplier_payment = 0
        total_lot_payment = 0
        total_detail_payments = 0

        dict_data = {'header': {}, 'lot_header': {}, 'detail': {}, 'lot_footer': {}, 'footer': {}}

        dict_data['header'].update(self.header(lot_payment_santander[0].payment_mode_id))

        for rec_lot_payment in lot_payment_santander:

            total_lot_payment += 1
            total_detail_payment = 0

            dict_data['lot_header'].update(self.lot_header(rec_lot_payment, total_lot_payment))

            for rec_lot_payment_line in rec_lot_payment.invoice_installment_ids:

                total_detail_payment += 1
                total_detail_payments += 1

                total_value_supplier_payment += rec_lot_payment_line.credit

                dict_data['detail'].update(self.detalhe(rec_lot_payment_line, total_detail_payment, total_lot_payment))

            dict_data['lot_footer'].update(self.lot_trailer(total_lot_payment, total_detail_payment, total_value_supplier_payment))

        dict_data['footer'].update(self.trailer(total_lot_payment, total_detail_payments))

        result = self.env['file.export.layout'].create_file('RemessaPagFornecedorSantander', dict_data)

        # Convert Hours
        w_timezone = self.env['res.users'].browse(self._uid).tz
        now = datetime.now(pytz.timezone(w_timezone))
        now_utc = datetime.today()

        filename = 'REM_%s_%04d%02d%02d_%02d%02d%02d.txt' % (rec_lot_payment_line.payment_mode_id.bank_account_id.bank_id.bic,
                                                             now.year,
                                                             now.month,
                                                             now.day,
                                                             now.hour,
                                                             now.minute,
                                                             now.second)

        encoded_result = base64.b64encode(result)

        self.env['bank.file'].create({'cnab_file': encoded_result, 'filename': filename, 'file_type': 'remessa_pagfor', 'date_time': now_utc, 'bank_id': rec_lot_payment_line.payment_mode_id.bank_account_id.bank_id.id})
