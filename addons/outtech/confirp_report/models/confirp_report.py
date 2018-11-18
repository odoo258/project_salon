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

from odoo import fields, models, _, api
from calendar import monthrange
from datetime import datetime
import base64
import pytz

class ConfirpReport(models.Model):
    _name = 'confirp.report'

    def _get_company(self):
        company_id = self.env.user.company_id
        return company_id

    company_id = fields.Many2one('res.company', 'Company', required=True, default=_get_company, readonly=True)
    journal_id = fields.Many2one('account.journal', 'Journal', required=True)
    period_id = fields.Date(string='Date Start', required=True)
    period_end_id = fields.Date(string='Date End', required=True)

    def cofirp_report(self):
        dict_data = {'header': {}, 'detail': {}, 'footer': {}}
        confirp_file = []
        debit = ''
        credit = ''

        move_date = datetime.strptime(self.period_id, "%Y-%m-%d")
        start_date = datetime.strptime('%s-%s-%s' % (move_date.year, move_date.month, '01'), '%Y-%m-%d')
        month_range = monthrange(move_date.year, move_date.month)
        final_date = datetime.strptime('%s-%s-%s' % (move_date.year, move_date.month, month_range[1]), '%Y-%m-%d')

        account_move_ids = self.env['account.move'].search([('company_id','=',self.env.user.company_id.id),('date','>=',start_date),('date','<=',final_date),('journal_id','=',self.journal_id.id)])
        for account_move in account_move_ids:
            company_name = self.env.user.company_id.name[0:4]
            account_date = datetime.strptime(account_move.date, "%Y-%m-%d")
            account_day = account_date.day
            account_month = account_date.month
            account_year = account_date.year
            journal = account_move.journal_id

            if journal.type == 'bank':
                if journal.bank_id:
                    bank_code = journal.bank_id.bic
            else:
                bank_code = ''

            # move_ids = self.env['account.move.line'].search([('move_id','=',account_move.id)])
            for move in account_move.line_ids:
                if move.credit:
                    credit = move.credit
                if move.debit:
                    debit = move.debit

            report_line = {account_move.name: {
                'CodEmpresa': company_name,
                'DiaLancamento': account_day,
                'MesLancamento': account_month,
                'AnoLancamento': account_year,
                'NumNotaFiscal': '',
                'ContaDebito': 54321,
                'EntradaSaida': 'E',
                'Banco': bank_code,
                'CentroCusto': '',
                'Valor': debit,
                'Historico': account_move.ref,
                'PadraoSistema': '',
                'ContaCredito': 12345,
            }}
            dict_data['detail'].update(report_line)

        confirp_report_txt = self.env['file.export.layout'].create_file('RelatorioConfirp', dict_data)

        obj_ir_attachment = self.env['ir.attachment']
        w_timezone = self.env['res.users'].browse(self._uid).tz
        now = datetime.now(pytz.timezone(w_timezone))

        src_ir_attachment = obj_ir_attachment.search([('res_model', '=', 'confirp.report'), ('res_id', '=', self.id)])

        filename = 'CONFIRP_%04d%02d%02d_%02d%02d%02d.txt' % (now.year,
                                                          now.month,
                                                          now.day,
                                                          now.hour,
                                                          now.minute,
                                                          now.second)

        if src_ir_attachment:
            attach_val = {
                'name': filename,
                'datas_fname': filename,
                'datas': base64.b64encode(confirp_report_txt.encode('ascii', 'replace'))
            }
            obj_ir_attachment.write(src_ir_attachment, attach_val)
        else:
            attach_vals = {'name': filename,
                           'datas_fname': filename,
                           'datas': base64.b64encode(confirp_report_txt.encode('ascii', 'replace')),
                           'file_type': format,
                           'res_model': 'confirp.report',
                           'res_id': self._uid
                           }

            obj_ir_attachment.create(attach_vals)

        confirp_report_download = self.env['confirp.report.download'].create({
            'data': base64.b64encode(confirp_report_txt.encode('ascii', 'replace')), 'filename': filename})

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'confirp.report.download',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': confirp_report_download.id,
            'views': [(False, 'form')],
            'target': 'new'
        }

class ConfirpReportDownload(models.Model):
    _name = 'confirp.report.download'

    filename = fields.Char('Filename', invisible=True, filename="filename")
    data = fields.Binary('File', readonly=True)




