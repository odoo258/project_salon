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
#domain=[('resale', '=', True)]
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import re

class ResUsers(models.Model):
    _inherit = 'res.users'

    is_master = fields.Boolean('User Master')
    user_resaller = fields.Boolean('User Resaller')

    @api.multi
    def write(self, vals):
        if 'password' in vals:
            self.partner_id.write({'password':vals['password']})
        return super(ResUsers, self).write(vals)


    @api.model
    def create(self, vals):
        user = super(ResUsers, self).create(vals)
        if user.partner_id:
            user.partner_id.write({'password': vals['password']})
        return user