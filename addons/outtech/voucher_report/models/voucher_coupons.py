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
from datetime import date

class VoucherCoupons(models.Model):
    _name = "voucher.coupons"

    @api.model
    def _get_company(self):
        user = self.env['res.users'].sudo().browse(self._uid)
        if user:
            return user.company_id.id

    @api.model
    def _get_user(self):
        user = self.env['res.users'].sudo().browse(self._uid)
        if user:
            return user.id

    @api.model
    def _get_date_today(self):
        return date.today()

    @api.model
    def _get_default_name(self):
        return self.env['ir.sequence'].next_by_code('voucher.coupons')

    @api.model
    def _get_rule(self):
        rule = self.env['voucher.coupons.config'].search([('active','=',True)])
        if rule:
            self.rule = rule.name
            return rule.name
        else:
            return ""

    name = fields.Char(string='Protocol', default=_get_default_name)
    protocol = fields.Char(string='Protocol')
    company_id = fields.Many2one('res.company', string='Company', default=_get_company)
    user_id = fields.Many2one('res.users', string='User', default=_get_user)
    date = fields.Date(string="Date", default=_get_date_today)
    date_limit = fields.Date(string="Date Limit", required=True)
    partner_id = fields.Many2one('res.partner', string='Customer', domain="[('customer','=',True)]", required=True)
    amount = fields.Float(string="Amount", required=True)
    rule = fields.Text('Rules', compute=_get_rule)
    state = fields.Selection([('created','Created'),('used','Used')],string='State', default='created')

    @api.onchange('name')
    def onchange_protocol(self):
        self.protocol = self.name
        return {}

    @api.model
    def create(self, vals):
        vals['name'] = vals['protocol']
        return super(VoucherCoupons, self).create(vals)

    def button_confirm(self):
        return self.write({'state':'used'})

class VoucherCouponsCofing(models.Model):
    _name = "voucher.coupons.config"

    name = fields.Text(string='Regra')
    active = fields.Boolean(string='Active')

    _sql_constraints = [
        ('active_rule_uniq', 'unique(active)', "Only one rule for voucher")
    ]
