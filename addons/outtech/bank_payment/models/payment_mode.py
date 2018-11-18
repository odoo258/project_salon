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

from odoo import fields, models

class PaymentMode(models.Model):
    _name = 'payment.mode'
    _inherit = 'payment.mode'

    generate_bank_payment = fields.Boolean(string='Generate Bank Payment', default=0)
    generate_lot_payment = fields.Boolean(string='Generate Lot of Payment', default=0)
    layout_remessa = fields.Many2one('file.export.layout', string='Layout of Remessa')
    layout_retorno = fields.Many2one('file.import.layout', string='Layout of Retorno')
    type_banking_billing = fields.Selection([('REG','Registrada'), ('SRG','Sem Registro'), ('ESC','Escritural')], string='Type Banking Billing')
    transmission_code = fields.Char(string='Transmission Code')
    writeoff_account_id = fields.Many2one('account.account', string="Difference Account")
