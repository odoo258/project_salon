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

from odoo import api, fields, models, exceptions, _

class ResUsers(models.Model):
    _inherit = "res.users"

    @api.constrains('user_password')
    def _onchange_user_password(self):
        if self.user_password:
            for char in self.user_password:
                if not char.isdigit():
                    raise exceptions.ValidationError(_('O campo Senha de Usuário deve conter apenas números'))
        return True

    @api.model
    def verify_password(self):
        user = self.env['res.users'].browse(self.env.uid)
        if user.user_allowed:
            return user
        else:
            return False


    percent = fields.Float(string='Percentage', default=0)
    percent = fields.Float(string='Percentage', default=0)
    date_validate = fields.Date(string='Validate Date')
    user_allowed = fields.Boolean(string='Is Allowed')
    user_password = fields.Char(string='User Password', size=8)
    discount_permission_id = fields.Many2one('discount.permission', string='Discount Permission')

