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

from datetime import date, datetime
from openerp import api, fields, models

class CashFlowWizard(models.TransientModel):
    _inherit = 'account.cash.flow.wizard'

    start_date = fields.Date(string="Start Date", required=True, default=fields.date.today())

    @api.multi
    def button_calculate(self):
        cashflow_id = self.env['account.cash.flow'].create({
            'start_date': self.start_date,
            'end_date': self.end_date,
            'start_amount': self.start_amount,
        })
        cashflow_id.action_calculate_report()

        if not self.print_report:
            return self.env['report'].get_action(
                cashflow_id.id, 'account_cash_flow.main_template_cash_flow')

        dummy, action_id = self.env['ir.model.data'].get_object_reference(
            'account_cash_flow', 'account_cash_flow_report_action')
        vals = self.env['ir.actions.act_window'].browse(action_id).read()[0]
        vals['domain'] = [('cashflow_id', '=', cashflow_id.id)]
        vals['context'] = {'search_default_cashflow_id': cashflow_id.id}
        return vals