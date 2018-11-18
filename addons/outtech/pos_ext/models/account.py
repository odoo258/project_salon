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

from odoo import fields, api, models, _

class AccountMove(models.Model):
    _name = 'account.move'
    _inherit = 'account.move'

    return_tef = fields.Text(string="TEF Return", readonly=True)
    authorization_number = fields.Char(string="Authorization Number", readonly=True)

    @api.model
    def create(self, vals):
        move = super(AccountMove, self).create(vals)
        return move

class AccountMoveLine(models.Model):
    _name = 'account.move.line'
    _inherit = 'account.move.line'

    authorization_number_rel = fields.Char(related='move_id.authorization_number', string='Authorization Number')