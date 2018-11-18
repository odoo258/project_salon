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
from odoo.exceptions import ValidationError
from datetime import date, datetime, timedelta

class AccountJournal(models.Model):
    _inherit = "account.journal"

    accepts_return = fields.Boolean('Accepts Return')
    payment_wallet = fields.Boolean('Payment with Wallet')
    pay_installments = fields.Boolean('Allow payment in installments')
    installments = fields.Many2one("monthly.installments", "Up To Installments")
    payment_mode_id = fields.Many2one("payment.mode", "Default Payment Mode")
    is_tef = fields.Boolean(string='Is Tef')
    card_banner_ids = fields.One2many('card.banner', 'journal_id', string='Card Banner')
    operation_code = fields.Char(string='Operation Code')
    is_contingency = fields.Boolean(string='Is Contingency')
    banner_name = fields.Char(string='Banner Name')
    range_days_maturity_date_debit = fields.Integer(string='Range of Days to Maturity Date of Instalments Debit')
    range_days_maturity_date_credit = fields.Integer(string='Range of Days to Maturity Date of Instalments Credit')
    range_days_maturity_date_credit_instalments = fields.Integer(string='Range of Days to Maturity Date of Credit Instalments')
    sat_payment_mode = fields.Selection([('01','DINHEIRO'),
                                         ('02','CHEQUE'),
                                         ('03','CARTAO CREDITO'),
                                         ('04','CARTAO DEBITO'),
                                         ('05','CREDITO LOJA'),
                                         ('10','VALE ALIMENTACAO'),
                                         ('11','VALE REFEICAO'),
                                         ('12','VALE PRESENTE'),
                                         ('13','VALE COMBUSTIVEL'),
                                         ('99','OUTROS')],"Sat Payment Mode", help="EX: DINHEIRO = '01'\
                                                                CHEQUE = '02'\
                                                                CARTAO_CREDITO = '03'\
                                                                CARTAO_DEBITO = '04'\
                                                                CREDITO_LOJA = '05'\
                                                                VALE_ALIMENTACAO = '10'\
                                                                VALE_REFEICAO = '11'\
                                                                VALE_PRESENTE = '12'\
                                                                VALE_COMBUSTIVEL = '13'\
                                                                OUTROS = '99'")

    @api.multi
    @api.constrains('is_tef', 'is_contingency')
    def _check_is_tef_is_contingency(self):
        for rec_id in self:
            if rec_id.is_tef and rec_id.is_contingency:
                raise ValidationError(_('The journal cannot have IS TEF and IS CONTIGENCY checked, choose only one.'))


    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if 'refund_id' in self._context:
            date_order = datetime.strptime(self.env['pos.order'].browse(self._context['refund_id']).date_order[:-9], '%Y-%m-%d')
            if str(date_order) != date.today().strftime("%Y-%m-%d 00:00:00"):
                args = [('accepts_return','=', True)]
        return super(AccountJournal, self).name_search(name, args, operator, limit)
        # if self.env['pos.order'].browse(self._context['refund_id']).date_order == datetime.today ():
        #     domain = [('journal_id', operator, dinheiro)]

    #args = [['id', 'in', [44, 62]]]



class CardBanner(models.Model):
    _name = 'card.banner'

    name = fields.Char(string='Name', required=True)
    journal_id = fields.Many2one('account.journal', string='Journal')