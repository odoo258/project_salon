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
from odoo import models, fields


class Partner(models.Model):
    _inherit = 'res.partner'

    supplier_id = fields.Many2many('wizard.stock.history', 'supp_wiz_rel', 'wiz', 'supp', invisible=True)


class Category(models.Model):
    _inherit = 'product.category'

    obj = fields.Many2many('wizard.stock.history', 'categ_wiz_rel', 'wiz', 'categ', invisible=True)


class Warehouse(models.Model):
    _inherit = 'stock.warehouse'

    obj = fields.Many2many('wizard.stock.history',  'wh_wiz_rel', 'wiz', 'wh', invisible=True)





