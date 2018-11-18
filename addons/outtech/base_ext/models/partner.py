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

    zip = fields.Char()

    def _get_country(self):
        country_id = False
        user = self.env['res.users'].browse(self._uid)
        if user.company_id:
            country_id = user.company_id.country_id.id or False
        return country_id

    manufacturer = fields.Boolean(string='Is a Manufacturer')
    foreign = fields.Boolean(string='Foreign')
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict', default=_get_country)
    cnpj_cpf = fields.Char('CNPJ/CPF', size=18, copy=False, required=True)
    
    @api.one
    @api.constrains('cnpj_cpf', 'country_id', 'is_company')
    def _check_cnpj_cpf(self):
        if not self.foreign:
            country_code = self.country_id.code or ''
            if self.cnpj_cpf and country_code.upper() == 'BR':
                val = re.sub('[^0-9]', '', self.cnpj_cpf)
                count_value = 0
                for x in set(list(val)):
                    count_value = val.count(x)
                    if count_value == 11:
                        raise UserError(_(u'Verifique o CNPJ/CPF Números Iguais não permitidos'))
                if self.is_company:
                    if not fiscal.validate_cnpj(self.cnpj_cpf):
                        raise UserError(_(u'CNPJ inválido!'))
                elif not fiscal.validate_cpf(self.cnpj_cpf):
                    raise UserError(_(u'CPF inválido!'))
        return True

    @api.multi
    def zip_search(self, cep):
        self.zip = "%s-%s" % (cep[0:5], cep[5:8])
        res = self.env['br.zip'].search_by_zip(zip_code=self.zip)
        if res:
            self.update(res)
        else:
            return False

    @api.onchange('zip')
    def _onchange_zip(self):
        if self.zip and not self.foreign:
            zip = self.zip.replace('-','')
            if zip.replace('0','') == '':
                return {
                    'warning': {'title': 'Erro!', 'message': 'CEP não pode conter somente 0'},
                    'value': {'zip': None, }}

            if len(zip) != 8:
                return {
                    'warning': {'title': 'Erro!', 'message': 'O tamanho do CEP deve ser de 8 números'},
                    'value': {'zip': None, }
                }

            for char in zip:
                if char.isalpha():
                    return {
                        'warning': {'title': 'Erro!', 'message': 'O CEP não pode conter nenhuma letra'},
                        'value': {'zip': None, }
                    }

            res = self.zip_search(zip)
            if res == False:
                return {'warning': {'title': 'Erro!', 'message': 'CEP não encontrado'},
                    'value': {'zip': None, }}
        else:
            return {'value': {'zip': self.zip, }}

    @api.onchange('email')
    def _onchange_email(self):
        if self.email:
            a = self.email
            len_a = len(a)
            if len_a < 2:
                return {
                    'warning': {'title': 'Erro!', 'message': 'E-mail inválido'},
                    'value': {'email': None,}
                }

            if a[0] == '@' or a[(len_a - 1)] == '@':
                return {
                    'warning': {'title': 'Erro!', 'message': 'E-mail inválido'},
                    'value': {'email': None, }
                }
            elif a[0] == '.' or a[(len_a - 1)] == '.':
                return {
                    'warning': {'title': 'Erro!', 'message': 'E-mail inválido'},
                    'value': {'email': None, }
                }

            regex = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', a)
            if regex == None:
                return {
                    'warning': {'title': 'Erro!', 'message': 'E-mail inválido'},
                    'value': {'email': None,}
                }

            return {
                'value': {'email': a, }
            }

    @api.onchange('cnpj_cpf', 'foreign')
    def _onchange_cnpj_cpf(self):
        if not self.foreign:
            country_code = self.country_id.code or ''
            if self.cnpj_cpf and country_code.upper() == 'BR':
                val = re.sub('[^0-9]', '', self.cnpj_cpf)
                if len(val) == 14:
                    cnpj_cpf = "%s.%s.%s/%s-%s"\
                        % (val[0:2], val[2:5], val[5:8], val[8:12], val[12:14])
                    self.cnpj_cpf = cnpj_cpf
                elif not self.is_company and len(val) == 11:
                    count_value = 0
                    for x in set(list(val)):
                        count_value = val.count(x)
                        if count_value == 11:
                            raise UserError(_(u'Verifique o CNPJ/CPF Números Iguais não permitidos'))
                    cnpj_cpf = "%s.%s.%s-%s"\
                        % (val[0:3], val[3:6], val[6:9], val[9:11])
                    self.cnpj_cpf = cnpj_cpf
                else:
                    raise UserError(_(u'Verifique o CNPJ/CPF'))
        return {'value':{'cnpj_cpf': self.cnpj_cpf}}


    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        if 'uid' in self._context:
            user = self.env['res.users'].browse(self._context['uid'])
            if user.view_partners:
                if user.view_partners == 'customer':
                    args.append(['customer','=',True])
                elif user.view_partners == 'supplier':
                    args.append(['supplier','=',True])
                elif user.view_partners == 'both':
                    return super(ResPartner, self).search(args, offset=offset, limit=limit, order=order, count=count)
        return super(ResPartner, self).search(args, offset=offset, limit=limit, order=order, count=count)

class BrZip(models.Model):
    _inherit = "br.zip"

    @api.multi
    def search_by_zip(self, zip_code):
        zip_ids = self.zip_search_multi(zip_code=zip_code)
        if len(zip_ids) == 1:
            return self.set_result(zip_ids[0])
        else:
            return False