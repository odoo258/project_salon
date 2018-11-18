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
from odoo.addons.br_base.tools import fiscal
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
import re


class ResPartner(models.Model):
    _inherit = "res.partner"

    sale_lines = fields.One2many('sale.order.line', 'partner_id', 'Lines Sale Order')
    pos_lines = fields.One2many('pos.order.line', 'partner_id', 'Lines Sale Order')