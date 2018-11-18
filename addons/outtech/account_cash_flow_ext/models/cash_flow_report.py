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

from openerp import api, fields, models


class CashFlowReport(models.TransientModel):
    _inherit = 'account.cash.flow'

    start_date = fields.Date(string="Start Date", required=True, default=fields.date.today())

    @api.multi
    def calculate_moves(self):
        moveline_obj = self.env['account.move.line']
        moveline_ids = moveline_obj.search([
            '|',
            ('account_id.user_type_id.type', '=', 'receivable'),
            ('account_id.user_type_id.type', '=', 'payable'),
            ('reconciled', '=', False),
            ('move_id.state', '!=', 'draft'),
            ('company_id', '=', self.env.user.company_id.id),
            ('date_maturity', '<=', self.end_date),
            ('date_maturity', '>=', self.start_date),
        ])
        moves = []
        for move in moveline_ids:
            debit = move.credit - move.credit_cash_basis
            credit = move.debit - move.debit_cash_basis
            amount = move.debit - move.credit

            moves.append({
                'name': move.ref or move.name,
                'cashflow_id': self.id,
                'partner_id': move.partner_id.id,
                'journal_id': move.journal_id.id,
                'account_id': move.account_id.id,
                'line_type': move.account_id.internal_type,
                'date': move.date_maturity,
                'debit': debit,
                'credit': credit,
                'amount': amount,
            })
        return moves