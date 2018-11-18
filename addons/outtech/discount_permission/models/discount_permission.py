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

class DiscountPersmission(models.Model):
    _name = "discount.permission"

    def _check_confirmed(self):
        regs = self.search([('state','=','confirmed')])
        for i in regs:
            if i.id != self.id:
                return False
        return True

    name = fields.Char(string='Name')
    discount_permission_lines = fields.One2many('discount.permission.line', 'discount_permission_id', string='Discount Permission Lines')
    state = fields.Selection([('draft','Draft'),('confirmed','Confirmed'),('cancel','Canceled')], string='State', default='draft')

    _constraints = [
        (_check_confirmed, 'Exist other register confirmed!', []),
    ]

    def update_data(self):
        for l in self.discount_permission_lines:
            l.user_id.write({'value':l.value,'percent':l.percent,'date_validate':l.date_validate,'discount_permission_id':self.id})
        return True

    def confirm(self):
        for l in self.discount_permission_lines:
            l.user_id.write({'value':l.value,'percent':l.percent,'date_validate':l.date_validate,'discount_permission_id':self.id})
        return self.write({'state':'confirmed'})

    def cancel(self):
        for l in self.discount_permission_lines:
            l.user_id.write({'value':0,'percent':0,'date_validate':False,'discount_permission_id':False})
        return self.write({'state':'cancel'})

    def write(self,vals):
        self.update_data()
        return super(DiscountPersmission, self).write(vals)


class DiscountPersmissionLine(models.Model):
    _name = "discount.permission.line"

    name = fields.Char('Name')
    user_id = fields.Many2one('res.users', string='SalesPerson', required=True)
    percent = fields.Float(string='Percentage', required=True)
    value = fields.Float(string='Value')
    date_validate = fields.Date(string='Validate Date', required=True)
    discount_permission_id = fields.Many2one('discount.permission', string='Discount Permission')