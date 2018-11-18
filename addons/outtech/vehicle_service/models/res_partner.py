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

class ResPartner(models.Model):
    _inherit = 'res.partner'

    resale = fields.Boolean(string='Is a Reseller')
    sale_team = fields.Many2one('crm.team', string='Sale Team')
    qty_installers = fields.Integer(string='Installers', default=0)
    resale_location = fields.Many2one('stock.location', string='Resale Location')
    credit_card_name = fields.Char(string='Name')
    credit_card_number = fields.Char(string='Number')
    credit_card_display_number = fields.Char(string='Number')
    credit_card_month_expiration = fields.Integer(string='Month Expiration')
    credit_card_year_expiration = fields.Integer(string='Year Expiration')
    credit_card_security_code = fields.Char(string='Security Code', size=3)
    credit_card_payment_acquirer = fields.Many2one('payment.acquirer', string="Flag")
    user_plataforma = fields.Char('User Plataform')
    transactionKey = fields.Char('transactionKey')
    orderKey = fields.Char('orderKey')
    instantBuyKey = fields.Char('instantBuyKey')
    password = fields.Char('Password')
    gender = fields.Selection([('MALE','MALE'),('FEMALE','FEMALE')], 'Gender', required=True)
    birthdate = fields.Date('Birthdate', required=True)

    # def search(self, args, offset=0, limit=None, order=None, count=False):

    #     return super(ResPartner, self).search(args, offset=offset, limit=limit, order=order, count=count)

    @api.onchange('credit_card_display_number')
    def credit_card_display_number_change(self):

        if self.credit_card_display_number:
            val = re.sub('[^0-9]', '', self.credit_card_display_number)

            if not len(val) == 16:
                return {'warning': {'title': _('WARNING'), 'message': _('Invalid Number Credit Card!')}}
            else:
                return {'value': {'credit_card_number': val}}

        return {'value': {'credit_card_number': ''}}

    @api.model
    def create(self, vals):

        if 'credit_card_display_number' in vals and vals['credit_card_display_number']:

            val = re.sub('[^0-9]', '', vals['credit_card_display_number'])

            if not 'XXXX-XXXX-XXXX-' in vals['credit_card_display_number'] and not len(val) == 16:
                raise UserError(_('WARNING'), _('Invalid Number Credit Card!'))

            if not 'XXXX-XXXX-XXXX-' in vals['credit_card_display_number']:
                vals['credit_card_display_number'] = 'XXXX-XXXX-XXXX-%s' % (val[12:16])
            else:
                vals['credit_card_display_number'] = 'XXXX-XXXX-XXXX-%s' % (val)

        return super(ResPartner, self).create(vals)

    @api.multi
    def write(self, vals):

        if 'credit_card_display_number' in vals:

            val = re.sub('[^0-9]', '', vals['credit_card_display_number'])

            if not 'XXXX-XXXX-XXXX-' in vals['credit_card_display_number'] and not len(val) == 16:
                raise UserError(_('WARNING'), _('Invalid Number Credit Card!'))

            if not 'XXXX-XXXX-XXXX-' in vals['credit_card_display_number']:
                vals['credit_card_display_number'] = 'XXXX-XXXX-XXXX-%s' % (val[12:16])
            else:
                vals['credit_card_display_number'] = 'XXXX-XXXX-XXXX-%s' % (val)

        return super(ResPartner, self).write(vals)

class ResPartnerCreditCard(models.Model):
    _name = 'res.partner.credit.card'

    credit_card_name = fields.Char(string='Name')
    credit_card_number = fields.Char(string='Number')
    credit_card_month_expiration = fields.Integer(string='Month Expiration')
    credit_card_year_expiration = fields.Integer(string='Year Expiration')
    credit_card_security_code = fields.Char(string='Security Code', size=3)
    credit_card_payment_acquirer = fields.Many2one('payment.acquirer', string="Flag")

    def create(self, vals):
        partner_id = self.env['res.users'].browse(self._context['uid']).partner_id
        if partner_id:
            partner_id.write(vals)
        else:
            raise UserError(_('Error in Create'))
        return super(ResPartnerCreditCard, self).create(vals)