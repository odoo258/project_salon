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

from odoo import fields, models, _, api

class AccountMoveLine(models.Model):
    _name = 'account.move.line'
    _inherit = 'account.move.line'

    def get_status(self):

        for line in self:

            if line.full_reconcile_id:

                line.status = 'paid'

            elif line.status_aux:

                line.status = 'confirmed'

            else:
                line.status = 'open'


    status = fields.Selection([('open','Open'),('confirmed','Confirmed'),('paid','Paid')], compute='get_status', string='Status')
    status_aux = fields.Boolean(string='Status Auxiliary', default=0)
    bank_payment_id = fields.Many2one('bank.payment', string='Bank Payment')
    lot_payment_id = fields.Many2one('lot.payment', string='Lot of Payment')
    bank_slip_bar_code = fields.Char(string='Bank Slip Bar Code')
    reference_code = fields.Char(string='Reference Code')

    def button_bar_code_number(self):

        return {
            'name': _('Include Bar Code'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.move.line.bank.slip',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',

        }

class AccountMoveLineBankSlip(models.Model):
    _name = 'account.move.line.bank.slip'

    number = fields.Char('Number Bar Code')

    def button_save_bar_code_number(self):

        if 'active_id' in self._context:
            self.env['account.move.line'].browse(self._context['active_id']).write({'bank_slip_bar_code':self.number})

        return {'type': 'ir.actions.act_window_close'}

