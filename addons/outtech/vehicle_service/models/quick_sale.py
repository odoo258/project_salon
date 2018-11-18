# -*- coding: utf-8 -*-
# encoding: utf-8
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

from odoo.addons.br_base.tools import fiscal
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date
from openerp import http
import requests as req
from unicodedata import normalize
import re
import requests
import logging
import json
_logger = logging.getLogger(__name__)

class QuickSale(models.Model):
    _name = "quick.sale"
    _inherit = ['mail.thread']

    def _get_user(self):
        if 'uid' in self._context:
            return self._context['uid']
        else:
            return False

    def _get_resale(self):
        if 'uid' in self._context:
            user = self.env['res.users'].sudo().browse(self._context['uid'])
            if user.sale_team_id:
                resale = self.env['res.partner'].sudo().search([('sale_team','=',user.sale_team_id.id)])
                if len(resale) != 1:
                    raise UserError(_('Verificar Equipe de Venda em Revenda!'))
                if resale:
                    res = resale.id
                else:
                    raise UserError(_('Any resale register!'))
            else:
                raise UserError(_('Any resale for user!'))
            return res
        else:
            return False

    name = fields.Char(string="Code", readonly=True)
    is_company_partner = fields.Boolean(string="Is Company", default=False)
    date = fields.Datetime(string="Date", readonly=True)
    cnpj_cpf_partner = fields.Char(string="CNPJ/CPF")
    name_partner = fields.Char(string="Name", required=True)
    zip_code_partner = fields.Char(string="Zip Code")
    street_partner = fields.Char(string="Street")
    number_partner = fields.Char(string="Number")
    street2_partner = fields.Char(string="Street2")
    district_partner = fields.Char(string="District")
    country_id_partner = fields.Many2one('res.country', string="Country")
    state_id_partner = fields.Many2one('res.country.state', string="State")
    city_id_partner = fields.Many2one('res.state.city', string="City")
    phone_partner = fields.Char(string="Phone")
    mobile_partner = fields.Char(string="Mobile")
    email_partner = fields.Char(string="E-Mail/Login", required=True)
    password = fields.Char(string="Password")
    confirmpassword = fields.Char(string="Confirm Password")
    name_credit_card = fields.Char(string="Name")
    number_credit_card = fields.Char(string="Number", size=16)
    display_number_credit_card = fields.Char(string="Number", size=19)
    credit_card_month_expiration = fields.Char(string='Month Expiration', size=2)
    credit_card_year_expiration = fields.Char(string='Year Expiration', size=4)
    security_code_credit_card = fields.Char(string="Security Code", size=3)
    payment_acquirer_credit_card = fields.Many2one('payment.acquirer', string="Flag")
    category_id_vehicle = fields.Many2one('vehicle.category', string="Category")
    manufacturer_id_vehicle = fields.Many2one('vehicle.manufacturer', string="Manufacturer")
    model_id_vehicle = fields.Many2one('vehicle.model', string="Model")
    year_id_vehicle = fields.Many2one('vehicle.year', string="Year")
    owner_name_vehicle = fields.Char(string='Owner Name')
    plate_vehicle = fields.Char(string='Plate', size=8)
    renavam_vehicle = fields.Char(string='Renavam')
    product_id_product = fields.Many2one('product.product', string='Product', readonly=True)
    plan_id_product = fields.Many2one('product.product', string='Plan')
    price_product = fields.Float(string="Price", readonly=True)
    monthly_payment = fields.Float(string="Monthly Payment", readonly=True)
    state = fields.Selection([('draft','Draft'),('waiting_confirmation','Waiting Confirmation'),('confirmed','Confirmed'),('waiting_payment','Waiting Payment'),('payment_error','Payment Error'),('user_error','Paid/Not user Register'),('paid','Paid'),('scheduled','Scheduled'),('done','Done')], string='State', default='draft')
    qty_plots = fields.Selection([('1','In cash'),('2','2 - Plots'),('3','3 - Plots'),('4','4 - Plots'),('5','5 - Plots'),('6','6 - Plots')], string='Payment Form', required=True, default='1')
    installation_id = fields.Many2one('installation.schedule', string='Installation')
    log_ids = fields.One2many('account.invoice.log', 'quick_sale_id', 'Logs')

    user_id = fields.Many2one('res.users', string='User', default=_get_user)
    resale_id = fields.Many2one('res.partner', string='Resale' , default=_get_resale)
    gender = fields.Selection([('MALE','MALE'),('FEMALE','FEMALE')], 'Gender', required=True)
    birthdate = fields.Date('Birthdate', required=True)
    register = fields.Boolean(string="Is Resgister", default=False)

    @api.multi
    def button_user(self):
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        partner = self.env["res.partner"].sudo().search([('cnpj_cpf','=',self.cnpj_cpf_partner)])
        cnpj_cpf = re.sub("[^0-9]", "", self.cnpj_cpf_partner)
        try:
            #Cadastro Plataforma
            dict_user = {
                "user": {
                    "login" : self.email_partner,
                    "name" : self.name_partner,
                    "password" : self.password, #A senha deve conter entre 8 e 32 caracteres.
                    "confirmPassword" : self.password, #A senha deve conter entre 8 e 32 caracteres.
                    "cpfCnpj" : cnpj_cpf, #O CPF/CNPJ informado não corresponde a um CPF/CNPJ válido. Informe apenas os números sem barras, pontos ou hífens
                    "email" : self.email_partner,
                    "gender" : self.gender,
                    "birthDate" : "%sT00:00:00" % self.birthdate,
                    "brand": "6713276314419200"
                        },
                "origin": 'ERP'
                }


            url_user = "%s/api/signin/" % self.user_id.company_id.url_api
            json_user = json.dumps(dict_user)
            user = requests.post(url_user, data=json_user, headers=headers)
            _logger.info(u'User - %s', user.text)
            if user.status_code not in [200,201]:
                self.env["account.invoice.log"].sudo().create({"log":u"Problema com Usuario - %s" % normalize('NFKD', eval(user.text)['message'].decode('utf-8')).encode('ASCII','ignore'), "quick_sale_id":self.id})
                self.sudo().write({"state":"user_error"})
                return False
            else:
                self.env["account.invoice.log"].sudo().create({"log":u"Cadastra de Usuario com Sucesso","quick_sale_id":self.id})
                self.sudo().write({"state":"paid"})
                if partner:
                    partner.sudo().write({
                                              "user_plataforma": str(eval(user.text)["user"]["id"])
                                                 })
                self.create_user()
                return True

        except Exception, m:
            self.env["account.invoice.log"].sudo().create({"log":u"Problema com Usuario - %s" % m, "quick_sale_id":self.id})
            self.sudo().write({"state":"user_error"})
            return False

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        if 'uid' in self._context:
            user = self.env['res.users'].browse(self._context['uid'])
            resale_manager = self.env['crm.team'].search([('user_id','=',user.id)])
            if not user.is_master and not args:
                args.append(['user_id','=',user.id])
            if resale_manager:
                user_team = resale_manager.member_ids.ids
                user_team.append(user.id)
                args.append(['user_id','in',user_team])
        return super(QuickSale, self).search(args, offset=offset, limit=limit, order=order, count=count)

    @api.onchange('renavam_vehicle')
    def renavam_vehicle_change(self):
        if self.renavam_vehicle:
            for char in self.renavam_vehicle:
                if not char.isdigit():
                    return {'value': {'renavam_vehicle': ''}, 'warning': {'title': _('Warning'), 'message': _('Renavam must contain only numbers.')}}
            else:
                return {'value': {'renavam_vehicle': self.renavam_vehicle}}
        else:
            return {'value': {}}

    @api.onchange('security_code_credit_card')
    def security_code_credit_card_change(self):
        if self.security_code_credit_card:
            for char in self.security_code_credit_card:
                if not char.isdigit():
                    return {'value': {'security_code_credit_card': ''}, 'warning': {'title': _('Warning'),
                                                                                     'message': _(
                                                                                         'Credit card CSV must contain only numbers.')}}
            else:
                if len(self.security_code_credit_card) < 3:
                    return {'value': {'security_code_credit_card': ''}, 'warning': {'title': _('Warning'),
                                                                                    'message': _(
                                                                                        'Credit card CSV must contain 3 digits.')}}
                return {'value': {'security_code_credit_card': self.security_code_credit_card}}
        else:
            return {'value': {}}

    @api.onchange('credit_card_month_expiration')
    def credit_card_month_expiration_change(self):
        if self.credit_card_month_expiration:
            for char in self.credit_card_month_expiration:
                if not char.isdigit():
                    return {'value': {'credit_card_month_expiration': ''}, 'warning': {'title': _('Warning'),
                                                                                    'message': _(
                                                                                        'Credit card expiration month must contain only numbers.')}}
            else:
                if float(self.credit_card_month_expiration) < 1 or float(self.credit_card_month_expiration) > 12:
                    return {'value': {'credit_card_month_expiration': ''}, 'warning': {'title': _('Warning'),
                                                                                       'message': _(
                                                                                           'Credit card expiration month be greater than 1 and lower than 12.')}}
                elif len(self.credit_card_month_expiration) == 1:
                    return {'value': {'credit_card_month_expiration': '0%s' % (self.credit_card_month_expiration)}}
                else:
                    return {'value': {'credit_card_month_expiration': self.credit_card_month_expiration}}
        else:
            return {'value': {}}

    @api.onchange('credit_card_year_expiration')
    def credit_card_year_expiration_change(self):
        if self.credit_card_year_expiration:
            for char in self.credit_card_year_expiration:
                if not char.isdigit():
                    return {'value': {'credit_card_year_expiration': ''}, 'warning': {'title': _('Warning'),
                                                                                       'message': _(
                                                                                           'Credit card expiration year must contain only numbers.')}}
            else:
                if len(self.credit_card_year_expiration) == 2:
                    return {'value': {'credit_card_year_expiration': '20%s' % (self.credit_card_year_expiration)}}
                elif len(self.credit_card_year_expiration) < 4:
                    return {'value': {'credit_card_year_expiration': ''}, 'warning': {'title': _('Warning'),
                                                                                      'message': _(
                                                                                          'Credit card expiration year must contain 4 digits.')}}
                else:
                    return {'value': {'credit_card_year_expiration': self.credit_card_year_expiration}}
        else:
            return {'value': {}}

    @api.onchange('manufacturer_id_vehicle')
    def manufacturer_id_vehicle_change(self):
        return {'value': {'model_id_vehicle': '', 'year_id_vehicle': '','product_id_product':'','price_product': 0.00,'monthly_payment': 0.00}}\

    @api.onchange('manufacturer_id_vehicle')
    def manufacturer_id_vehicle_change(self):
        return {'value': {'model_id_vehicle': '', 'year_id_vehicle': '','product_id_product':'','price_product': 0.00,'monthly_payment': 0.00}}

    @api.onchange('model_id_vehicle')
    def model_id_vehicle_change(self):
        return {'value': {'year_id_vehicle': '','product_id_product':'','price_product': 0.00,'monthly_payment': 0.00}}

    @api.onchange('year_id_vehicle')
    def year_id_vehicle_change(self):
        if self.year_id_vehicle.id:
            return {'value': {'product_id_product':self.model_id_vehicle.product_id.id,'price_product': self.model_id_vehicle.product_id.list_price}}
        else:
            return {'value': {}}

    @api.onchange('plan_id_product')
    def plan_id_product_change(self):
        if self.plan_id_product.id:
            return {'value': {'monthly_payment': self.plan_id_product.list_price}}
        else:
            return {'value': {}}

    @api.onchange('cnpj_cpf_partner')
    def cnpj_cpf_partner_change(self):

        vals = {}

        if self.cnpj_cpf_partner:
            if self.is_company_partner:
                cnpj_cpf = re.sub('[^0-9]', '', self.cnpj_cpf_partner)
                if len(cnpj_cpf) == 14:
                    cnpj_cpf = '' + cnpj_cpf[:2] + '.' + cnpj_cpf[2:5] + '.' + cnpj_cpf[5:8] + '/' + cnpj_cpf[8:12] + '-' + cnpj_cpf[12:14]
                else:
                    return {'warning':{'title': _('Warning'), 'message': _('CNPJ do not have 14 characters.')}}
                if not fiscal.validate_cnpj(cnpj_cpf):
                    raise UserError(_(u'CNPJ inválido!'))
            else:
                cnpj_cpf = re.sub('[^0-9]', '', self.cnpj_cpf_partner)
                if len(cnpj_cpf) == 11:
                    cnpj_cpf = '' + cnpj_cpf[0:3] + '.' + cnpj_cpf[3:6] + '.' + cnpj_cpf[6:9] + '-' + cnpj_cpf[9:11]
                else:
                    return {'warning': {'title': _('Warning'), 'message': _('CPF do not have 11 characters.')}}
                if not fiscal.validate_cpf(cnpj_cpf):
                    raise UserError(_(u'CPF inválido!'))
            res_partner_ids = self.env['res.partner'].search([('cnpj_cpf','=',cnpj_cpf)])

            if res_partner_ids:
                res_partner_id = res_partner_ids[0]

                vals = {
                    'cnpj_cpf_partner': cnpj_cpf,
                    'name_partner': res_partner_id.name,
                    'zip_code_partner': res_partner_id.zip,
                    'street_partner': res_partner_id.street,
                    'number_partner': res_partner_id.number,
                    'street2_partner': res_partner_id.street2,
                    'district_partner': res_partner_id.district,
                    'country_id_partner': res_partner_id.country_id,
                    'state_id_partner': res_partner_id.state_id,
                    'city_id_partner': res_partner_id.city_id,
                    'phone_partner': res_partner_id.phone,
                    'mobile_partner': res_partner_id.mobile,
                    'email_partner': res_partner_id.email,
                    'name_credit_card': res_partner_id.credit_card_name,
                    'number_credit_card': res_partner_id.credit_card_number,
                    'display_number_credit_card': res_partner_id.credit_card_display_number,
                    'credit_card_month_expiration': res_partner_id.credit_card_month_expiration,
                    'credit_card_year_expiration': res_partner_id.credit_card_year_expiration,
                    'security_code_credit_card': res_partner_id.credit_card_security_code,
                    'payment_acquirer_credit_card': res_partner_id.credit_card_payment_acquirer,
                    'gender': res_partner_id.gender,
                    'birthdate': res_partner_id.birthdate,
                    'register': True,
                }
            else:
                vals = {
                    'cnpj_cpf_partner': cnpj_cpf,
                    'name_partner': '',
                    'zip_code_partner': '',
                    'street_partner': '',
                    'number_partner': '',
                    'street2_partner': '',
                    'district_partner': '',
                    'country_id_partner': '',
                    'state_id_partner': '',
                    'city_id_partner': '',
                    'phone_partner': '',
                    'mobile_partner': '',
                    'email_partner': '',
                    'name_credit_card': '',
                    'number_credit_card': '',
                    'display_number_credit_card': '',
                    'credit_card_month_expiration': '',
                    'credit_card_year_expiration': '',
                    'security_code_credit_card': '',
                    'payment_acquirer_credit_card': '',
                    'gender': '',
                    'birthdate': '',
                    'register': False,
                }

        return {'value': vals}

    @api.onchange('phone_partner')
    def phone_partner_change(self):

        if self.phone_partner:

            val = re.sub('[^0-9]', '', self.phone_partner)

            format_phone = '(' + val[0:2] + ') ' + val[2:6]+'-'+ val[6:]

            return {'value': {'phone_partner':format_phone}}

        return {'value': {}}

    @api.onchange('mobile_partner')
    def mobile_partner_change(self):

        if self.mobile_partner:

            val = re.sub('[^0-9]', '', self.mobile_partner)

            format_mobile = '(' + val[0:2] + ') ' + val[2:3] + ' ' + val[3:7] + '-' + val[7:]

            return {'value': {'mobile_partner':format_mobile}}

        return {'value': {}}

    @api.onchange('plate_vehicle')
    def plate_vehicle_partner_change(self):

        if self.plate_vehicle:

            plate_upper = self.plate_vehicle.upper()

            val = re.sub('[^A-Z0-9]', '', plate_upper)

            if not len(val) == 7:
                return {'warning': {'title': _('WARNING'),'message': _('Invalid Plate')}}

            for char in val[0:3]:
                if not char.isalpha():
                    return {'warning': {'title': _('WARNING'), 'message': _('Invalid Plate')}}

            for number in val[3:]:
                try:
                    int(number)
                except:
                    return {'warning': {'title': _('WARNING'), 'message': _('Invalid Plate')}}

            format_plate = val[0:3] + '-' + val[3:]

            return {'value': {'plate_vehicle': format_plate}}

        return {'value': {}}

    @api.onchange('zip_code_partner')
    def zip_code_partner_change(self):
        if self.zip_code_partner:
            self.ensure_one()

            obj_zip = self.env['br.zip']

            zip_ids = obj_zip.zip_search_multi(
                country_id=self.country_id_partner.id,
                state_id=self.state_id_partner.id,
                city_id=self.city_id_partner.id,
                district=self.district_partner,
                street=self.street_partner,
                zip_code=self.zip_code_partner,
            )
            if len(zip_ids) == 1:
                result = self._set_result_zip(zip_ids[0])

                return {'value': result}

        return {'value': {}}

    @api.onchange('display_number_credit_card')
    def display_number_credit_card_change(self):
        if not self.display_number_credit_card:
            return {'value': {'number_credit_card': ''}}

        if self.display_number_credit_card and not 'XXXX-XXXX-XXXX-' in self.display_number_credit_card:
            for char in self.display_number_credit_card:
                if not char.isdigit():
                    return {'value': {'display_number_credit_card': ''}, 'warning': {'title': _('Warning'),
                                                                                       'message': _(
                                                                                           'Credit card number must contain only numbers.')}}
            val = re.sub('[^0-9]', '', self.display_number_credit_card)

            if len(val) > 16 or len(val) < 16:
                return {'value': {'display_number_credit_card': ''}, 'warning': {'title': _('WARNING'), 'message': _('Credit Card number must contain 16 digits!')}}
            else:
                return {'value': {'number_credit_card': val, 'display_number_credit_card': val}}
        else:
            return {'value': {'number_credit_card': self.display_number_credit_card}}


    @api.multi
    def _set_result_zip(self, zip_obj=None):
        if zip_obj:
            zip_code = zip_obj.zip
            if len(zip_code) == 8:
                zip_code = '%s-%s' % (zip_code[0:5], zip_code[5:8])
            result = {
                'country_id_partner': zip_obj.country_id.id,
                'state_id_partner': zip_obj.state_id.id,
                'city_id_partner': zip_obj.city_id.id,
                'district_partner': zip_obj.district,
                'street_partner': ((zip_obj.street_type or '') + ' ' + (zip_obj.street or '')) if zip_obj.street_type else (zip_obj.street or ''),
                'zip_code_partner': zip_code,
            }
        else:
            result = {}
        return result

    @api.multi
    def _validate(self, vals):

        if not vals['cnpj_cpf_partner']:
            return _('CNPJ/CPF not found! This field is required!')

        if vals['is_company_partner']:
            if not fiscal.validate_cnpj(vals['cnpj_cpf_partner']):
                return _('CNPJ is not valid!')
        elif not fiscal.validate_cpf(vals['cnpj_cpf_partner']):
            return _('CPF is not valid!')

        if not vals['name_partner']:
            return _('Partner Name not found! This field is required!')

        if not vals['number_credit_card']:
            return _('Card Number not found! This field is required!')

        if not vals['email_partner']:
            return _('Email not found! This field is required!')

        if not vals['name_credit_card']:
            return _('Name Credit Card not found! This field is required!')

        if not vals['number_credit_card']:
            return _('Number Credit Card not found! This field is required!')

        if not vals['credit_card_month_expiration']:
            return 'Month Expiration Credit Card not found! This field is required!'

        if not vals['credit_card_year_expiration']:
            return 'Year Expiration Credit Card not found! This field is required!'

        if not vals['security_code_credit_card']:
            return _('Security Code Credit Card not found! This field is required!')

        if not vals['category_id_vehicle']:
            return _('Category Vehicle not found! This field is required!')

        if not vals['manufacturer_id_vehicle']:
            return _('Manufacturer Vehicle not found! This field is required!')

        if not vals['model_id_vehicle']:
            return _('Model Vehicle not found! This field is required!')

        if not vals['year_id_vehicle']:
            return _('Year Vehicle not found! This field is required!')

        if not vals['owner_name_vehicle']:
            return _('Owner Name Vehicle not found! This field is required!')

        if not vals['plate_vehicle']:
            return _('Plate Vehicle not found! This field is required!')

        if self.env['vehicle.partner'].search([('plate', '=', vals['plate_vehicle'])]):
            return _('Plate already registered!')

        if not vals['renavam_vehicle']:
            return _('Renavam Vehicle not found! This field is required!')

        if not vals['product_id_product']:
            return _('Product not found! This field is required!')

        if not vals['price_product']:
            return _('Price not found! This field is required!')

        if not vals['plan_id_product']:
            return _('Plan not found! This field is required!')

        if not vals['monthly_payment']:
            return _('Monthly Payment not found! This field is required!')

        return False

    @api.multi
    def try_payment(self):
        res = {}
        sale = self.env['sale.order'].search([('quick_sale_id','=',self.id)])
        inv = self.env['account.invoice'].sudo().search([('sale_id','=',sale.id)])[0]
        request_php = self.env['request.php'].firt_payment(inv, self)
        if request_php:
            res['warning'] = _(u'Pagamento Confirmado com Sucesso!')
        else:
            res['warning'] = _(u'Pagamento não confirmado, confira no Log de pagamento!')
        return res

    @api.multi
    def change_credit_card(self):
        dummy, view_id = self.env['ir.model.data'].get_object_reference('vehicle_service', 'change_credit_card_form')

        return {
            'name':_("Change Credit Card"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'change.credit.card',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
                'close_after_process': True
            }
        }

    @api.multi
    def confirm_button(self):

        vals = {
                'is_company_partner': self.is_company_partner,
                'cnpj_cpf_partner': self.cnpj_cpf_partner,
                'name_partner': self.name_partner,
                'email_partner': self.email_partner,
                'name_credit_card': self.name_credit_card,
                'number_credit_card': self.number_credit_card,
                'credit_card_month_expiration': self.credit_card_month_expiration,
                'credit_card_year_expiration': self.credit_card_year_expiration,
                'security_code_credit_card': self.security_code_credit_card,
                'payment_acquirer_credit_card': self.payment_acquirer_credit_card,
                'category_id_vehicle': self.category_id_vehicle,
                'manufacturer_id_vehicle': self.manufacturer_id_vehicle,
                'model_id_vehicle': self.model_id_vehicle,
                'year_id_vehicle': self.year_id_vehicle,
                'owner_name_vehicle': self.owner_name_vehicle,
                'plate_vehicle': self.plate_vehicle,
                'renavam_vehicle': self.renavam_vehicle,
                'product_id_product': self.product_id_product,
                'plan_id_product': self.plan_id_product,
                'price_product': self.price_product,
                'monthly_payment': self.monthly_payment,
            }

        res = self._validate(vals)

        if res:
            raise UserError(res)
        else:

            template_id = self.env['mail.template'].search([('model', '=', 'quick.sale'),('domain','=','sale')])

            if not template_id:
                raise UserError(_('There is no email template for sale confirmation'))

            mail_values = template_id.generate_email(self.id)

            br_ir = self.env['ir.config_parameter'].search([('key','=','web.base.url')])

            link = br_ir.value + '/email/return?' + 'quick_order=%s' %(str(self.id))

            link2 = 'email/return?' + 'quick_order=%s' %(str(self.id))

            body_html = mail_values['body_html'].replace('@link', link2)

            vals_email = {
                'subject':mail_values['subject'],
                'email_from':mail_values['email_from'],
                'email_to':mail_values['email_to'],
                'body_html':body_html,
                'auto_delete':False,
                'state':'outgoing',
                'model':mail_values['model'],
                'res_id':mail_values['res_id'],
            }

            self.env['mail.mail'].create(vals_email)

            return self.write({'state':'waiting_confirmation'})

    @api.multi
    def schedule_installation_button(self):

        br_sale_order = self.env['sale.order'].sudo().search([('quick_sale_id','=',self.id)])

        if br_sale_order:
            br_installation_schedule = self.env['installation.schedule'].sudo().search([('sale_order_id','=',br_sale_order.id)])

            if br_installation_schedule:

                dummy, view_id = self.env['ir.model.data'].sudo().get_object_reference('vehicle_service', 'installation_schedule_wizard_form')

                return {
                    'name': "Scheduling",
                    'view_mode': 'form',
                    'view_id': view_id,
                    'view_type': 'form',
                    'res_model': 'installation.schedule',
                    'res_id': br_installation_schedule.id,
                    'type': 'ir.actions.act_window',
                    'nodestroy': True,
                    'target': 'new',
                    'domain': '[]'
                }
            else:
                raise UserError(_('No scheduling linked to this sale'))

        else:
            raise UserError(_('No scheduling linked to this sale'))

        return True

    @api.model
    def create(self, vals):

        vals['name'] = self.env['ir.sequence'].next_by_code('quick.sale') or 'New'
        vals['date'] = fields.Datetime.now()

        if 'display_number_credit_card' in vals and vals['display_number_credit_card']:

            val = re.sub('[^0-9]', '', vals['display_number_credit_card'])

            if not 'XXXX-XXXX-XXXX-' in vals['display_number_credit_card'] and not len(val) == 16:
                raise UserError(_('WARNING'), _('Invalid Number Credit Card!'))

            if len(val) == 16:
                vals['display_number_credit_card'] = 'XXXX-XXXX-XXXX-%s' % (val[12:16])
            else:
                vals['display_number_credit_card'] = 'XXXX-XXXX-XXXX-%s' % (val)

        br_model_vehicle = self.env['vehicle.model'].browse(vals['model_id_vehicle'])
        br_product_product = self.env['product.product'].browse(vals['plan_id_product'])

        vals['product_id_product'] = br_model_vehicle.product_id.id
        vals['price_product'] = br_model_vehicle.product_id.list_price
        vals['monthly_payment'] = br_product_product.list_price

        return super(QuickSale, self).create(vals)

    @api.multi
    def write(self, vals):

        if 'display_number_credit_card' in vals:

            val = re.sub('[^0-9]', '', vals['display_number_credit_card'])

            if not 'XXXX-XXXX-XXXX-' in vals['display_number_credit_card'] and not len(val) == 16:
                raise UserError(_('WARNING'), _('Invalid Number Credit Card!'))

            if len(val) == 16:
                vals['display_number_credit_card'] = 'XXXX-XXXX-XXXX-%s' % (val[12:16])
            else:
                vals['display_number_credit_card'] = 'XXXX-XXXX-XXXX-%s' % (val)

        if 'model_id_vehicle' in vals:
            br_model_vehicle = self.env['vehicle.model'].browse(vals['model_id_vehicle'])
        else:
            br_model_vehicle = self.env['vehicle.model'].browse(self.model_id_vehicle.id)

        if 'plan_id_product' in vals:
            br_product_product = self.env['product.product'].browse(vals['plan_id_product'])
        else:
            br_product_product = self.env['product.product'].browse(self.plan_id_product.id)

        vals['product_id_product'] = br_model_vehicle.product_id.id
        vals['price_product'] = br_model_vehicle.product_id.list_price
        vals['monthly_payment'] = br_product_product.list_price

        return super(QuickSale, self).write(vals)

    @api.multi
    def force_confirm_button(self):
        return self.write({'state': 'confirmed'})

    @api.multi
    def quick_sale_process(self):

        obj_res_partner = self.env['res.partner']

        src_quick_sale = self.search([('state','=','confirmed')])

        for br_quick_sale in src_quick_sale:

            # Create or Edit Partner

            src_res_partner = obj_res_partner.search([('cnpj_cpf', '=', br_quick_sale.cnpj_cpf_partner)])

            vals_partner = {
                'cnpj_cpf': br_quick_sale.cnpj_cpf_partner,
                'name': br_quick_sale.name_partner,
                'zip': br_quick_sale.zip_code_partner,
                'street': br_quick_sale.street_partner,
                'number': br_quick_sale.number_partner,
                'street2': br_quick_sale.street2_partner,
                'district': br_quick_sale.district_partner,
                'country_id': br_quick_sale.country_id_partner.id,
                'state_id': br_quick_sale.state_id_partner.id,
                'city_id': br_quick_sale.city_id_partner.id,
                'phone': br_quick_sale.phone_partner,
                'mobile': br_quick_sale.mobile_partner,
                'email': br_quick_sale.email_partner,
                'credit_card_name': br_quick_sale.name_credit_card,
                'credit_card_display_number': br_quick_sale.number_credit_card,
                'credit_card_number': br_quick_sale.number_credit_card,
                'credit_card_month_expiration': br_quick_sale.credit_card_month_expiration,
                'credit_card_year_expiration': br_quick_sale.credit_card_year_expiration,
                'credit_card_security_code': br_quick_sale.security_code_credit_card,
                'credit_card_payment_acquirer': br_quick_sale.payment_acquirer_credit_card.id,
                'gender': br_quick_sale.gender,
                'birthdate': br_quick_sale.birthdate,
                'property_account_receivable_id':25,
                'property_account_payable_id':97,
            }

            if src_res_partner:

                res_partner_id = src_res_partner

                src_res_partner.write(vals_partner)

            else:
                vals_partner.update({'password':br_quick_sale.password})
                res_partner_id = obj_res_partner.create(vals_partner)

            # Create Vehicle

            vals_vehicle = {
                'partner_id': res_partner_id.id,
                'owner_name': br_quick_sale.owner_name_vehicle,
                'renavam': br_quick_sale.renavam_vehicle,
                'plate': br_quick_sale.plate_vehicle,
                'category_id': br_quick_sale.category_id_vehicle.id,
                'manufacturer_id': br_quick_sale.manufacturer_id_vehicle.id,
                'model_id': br_quick_sale.model_id_vehicle.id,
                'year_id': br_quick_sale.year_id_vehicle.id,
            }

            vehicle_id = self.env['vehicle.partner'].create(vals_vehicle)

            # Create Sale Order

            vals_sale_order = {
                'partner_id': res_partner_id.id,
                'team_id': self.resale_id.id,
                'user_id': self.user_id.id,
                'quick_sale_id': br_quick_sale.id
            }

            sale_order_id = self.env['sale.order'].create(vals_sale_order)

            # Create Sale Order Line

            vals_sale_order_line = {
                'product_id': br_quick_sale.product_id_product.id,
                'product_uom': br_quick_sale.product_id_product.uom_id.id,
                'order_id': sale_order_id.id,
                'tax_id':[(6, 0, br_quick_sale.product_id_product.taxes_id.ids)],
                'cofins_cst':'49',
                'pis_cst':'49'
            }

            self.env['sale.order.line'].create(vals_sale_order_line)

            # Confirm Sale Order

            sale_order_id.action_confirm()

            # Create invoice

            sale_order_id.action_invoice_create()

            # Link Schedule with Quick Sale

            src_installation_schedule = self.env['installation.schedule'].search([('sale_order_id','=',sale_order_id.id)])

            if src_installation_schedule:
                vals_quick_sale = {'installation_id': src_installation_schedule.id}

                src_installation_schedule.write({'vehicle_id':vehicle_id.id})
            else:
                vals_quick_sale = {'state': 'waiting_payment'}

            br_quick_sale.write(vals_quick_sale)

        return True


    @api.onchange('password')
    def password_change(self):
        if self.password:
            if len(self.password) < 8 or len(self.password) > 32:
                return {'warning': {'title': _('WARNING'), 'message': _('Password wrong 8 as 32')},'value':{'password':''}}
        return {}

    @api.onchange('confirmpassword')
    def confirmpassword_change(self):
        if self.confirmpassword:
            if len(self.confirmpassword) < 8 or len(self.confirmpassword) > 32:
                return {'warning': {'title': _('WARNING'), 'message': _('Confirm Password wrong 8 as 32')},'value':{'confirmpassword':''}}
            if self.password != self.confirmpassword:
                return {'warning': {'title': _('WARNING'), 'message': _('Confirm Password wrong')}, 'value':{'confirmpassword':''}}
        return {}

    @api.multi
    def create_user(self):
        # Create User
        user = self.env['res.users'].search([('login','=',self.email_partner)])
        partner = self.env["res.partner"].sudo().search([('cnpj_cpf','=',self.cnpj_cpf_partner)])
        if not user  and self.password:
            user_template = self.env['ir.config_parameter'].search([('key','=','auth_signup.template_user_id')])

            if user_template:
                temp_user = self.env['res.users'].browse(int(user_template.value))
                temp_user.copy(
                                    {
                                     'name': self.name_partner,
                                     'login': self.email_partner,
                                     'password': self.password,
                                     'partner_id': partner[0].id,
                                     'active': True,
                                     }
                                )
                return True
        else:
            return False

    @api.multi
    def quick_sale_process_auto(self):

        # Create or Edit Partner
        if self.state in ['waiting_confirmation']:
            src_res_partner = self.env['res.partner'].search([('cnpj_cpf', '=', self.cnpj_cpf_partner)])

            vals_partner = {
                'cnpj_cpf': self.cnpj_cpf_partner,
                'name': self.name_partner,
                'zip': self.zip_code_partner,
                'street': self.street_partner,
                'number': self.number_partner,
                'street2': self.street2_partner,
                'district': self.district_partner,
                'country_id': self.country_id_partner.id,
                'state_id': self.state_id_partner.id,
                'city_id': self.city_id_partner.id,
                'phone': self.phone_partner,
                'mobile': self.mobile_partner,
                'email': self.email_partner,
                'credit_card_name': self.name_credit_card,
                'credit_card_number': self.number_credit_card,
                'credit_card_display_number': self.display_number_credit_card,
                'credit_card_month_expiration': self.credit_card_month_expiration,
                'credit_card_year_expiration': self.credit_card_year_expiration,
                'credit_card_security_code': self.security_code_credit_card,
                'credit_card_payment_acquirer': self.payment_acquirer_credit_card.id,
                'gender': self.gender,
                'birthdate': self.birthdate,
                'property_account_receivable_id':25,
                'property_account_payable_id':97,
            }

            if src_res_partner:

                res_partner_id = src_res_partner

                src_res_partner.write(vals_partner)

            else:
                vals_partner.update({'password': self.password})
                res_partner_id = self.env['res.partner'].create(vals_partner)

            # # Create User
            # user = self.env['res.users'].search([('login','=',self.email_partner)])
            # if not user  and self.password:
            #     user_template = self.env['ir.config_parameter'].search([('key','=','auth_signup.template_user_id')])
            #
            #     if user_template:
            #         temp_user = self.env['res.users'].browse(int(user_template.value))
            #         temp_user.copy(
            #                             {
            #                              'name': self.name_partner,
            #                              'login': self.email_partner,
            #                              'password': self.password,
            #                              'partner_id': res_partner_id.id,
            #                              'active': True,
            #                              }
            #                         )

            # Create Vehicle

            vals_vehicle = {
                'partner_id': res_partner_id.id,
                'owner_name': self.owner_name_vehicle,
                'renavam': self.renavam_vehicle,
                'plate': self.plate_vehicle,
                'category_id': self.category_id_vehicle.id,
                'manufacturer_id': self.manufacturer_id_vehicle.id,
                'model_id': self.model_id_vehicle.id,
                'year_id': self.year_id_vehicle.id,
            }

            vehicle_id = self.env['vehicle.partner'].create(vals_vehicle)

            # Create Sale Order

            user_id = self.env['res.users'].search([('id','=',self.user_id.id)])

            vals_sale_order = {
                'partner_id': res_partner_id.id,
                'user_id': user_id.id,
                'team_id': user_id.sale_team_id.id,
                'quick_sale_id': self.id
            }

            sale_order_id = self.env['sale.order'].create(vals_sale_order)

            # Create Sale Order Line

            vals_sale_order_line = {
                'product_id': self.product_id_product.id,
                'product_uom': self.product_id_product.uom_id.id,
                'order_id': sale_order_id.id,
                'tax_id':[(6, 0, self.product_id_product.taxes_id.ids)],
                'cofins_cst':'99',
                'pis_cst':'99'
            }

            self.env['sale.order.line'].create(vals_sale_order_line)

            # Confirm Sale Order

            sale_order_id.action_confirm()

            # Create invoice

            sale_order_id.action_invoice_create()

            # Link Schedule with Quick Sale

            src_installation_schedule = self.env['installation.schedule'].search([('sale_order_id','=',sale_order_id.id)])

            if src_installation_schedule:
                vals_quick_sale = {'installation_id': src_installation_schedule.id}

                src_installation_schedule.write({'vehicle_id': vehicle_id.id})
            else:
                vals_quick_sale = {'state': 'waiting_payment'}

            self.write(vals_quick_sale)

            return {'sale_id': sale_order_id.id}
        else:
            return {'state': self.state}

class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):

        if 'model_id' in self._context:
            if self._context['model_id']:
                br_vehicle_model = self.env['vehicle.model'].browse(self._context['model_id'])
                args.insert(0, ('id', 'in', br_vehicle_model.plan_ids.ids))
            else:
                args.insert(0, ('id', '=', 0))

        return super(ProductProduct, self)._search(args, offset=offset, limit=limit, order=order, count=False, access_rights_uid=access_rights_uid)
