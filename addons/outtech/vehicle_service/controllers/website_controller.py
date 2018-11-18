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
import logging
from datetime import datetime
import re
import requests as req
import odoo
import json
from werkzeug import exceptions
from odoo.exceptions import UserError
from odoo import api, fields, models, registry, _
from odoo.http import request
from odoo.addons.website.models.website import slug
from odoo.addons.website.controllers.main import QueryURL
from openerp import http
from odoo.addons.website_form.controllers.main import WebsiteForm
from odoo.http import Controller
from datetime import date
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.website_sale.controllers.main import TableCompute
from odoo.addons.report.controllers.main import ReportController
from odoo.addons.web.controllers.main import Home
from unicodedata import normalize


_logger = logging.getLogger(__name__)

PPG = 20  # Products Per Page
PPR = 4   # Products Per Row

class WebsiteLogin(Home):

    @http.route(website=True, auth="public")
    def web_login(self, redirect=None, *args, **kw):
        response = super(WebsiteLogin, self).web_login(redirect=redirect, *args, **kw)
        if not redirect and request.params['login_success']:
            if request.env['res.users'].browse(request.uid).has_group('base.group_user'):
                redirect = '/web?' + request.httprequest.query_string
            elif request.env['res.users'].browse(request.uid).user_resaller:
                redirect = '/web?' + request.httprequest.query_string
            else:
                redirect = '/'
            return http.redirect_with_hash(redirect)
        return response

class ReportControllerInherit(ReportController):
    @http.route([
        '/report/<converter>/<reportname>',
        '/report/<converter>/<reportname>/<docids>',
    ], type='http', auth='user', website=True)
    def report_routes(self, reportname, docids=None, converter=None, **data):
        request.session.authenticate(request.session.db, request.session.login, request.session.password)
        report_obj = request.env['report']
        context = dict(request.env.context)

        if docids:
            docids = [int(i) for i in docids.split(',')]
        if data.get('options'):
            data.update(json.loads(data.pop('options')))
        if data.get('context'):
            # Ignore 'lang' here, because the context in data is the one from the webclient *but* if
            # the user explicitely wants to change the lang, this mechanism overwrites it.
            data['context'] = json.loads(data['context'])
            if data['context'].get('lang'):
                del data['context']['lang']
            context.update(data['context'])
        if converter == 'html':
            html = report_obj.with_context(context).sudo().get_html(docids, reportname, data=data)
            return request.make_response(html)
        elif converter == 'pdf':
            pdf = report_obj.with_context(context).sudo().get_pdf(docids, reportname, data=data)
            pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', len(pdf))]
            return request.make_response(pdf, headers=pdfhttpheaders)
        else:
            raise exceptions.HTTPException(description='Converter %s not implemented.' % converter)

class WebsiteController(http.Controller):
    @http.route(['/password/validate'], type='json', auth="public", methods=['POST'], csrf=False)
    def password_validate(self, **kwargs):
        password = kwargs['password']

        if len(password) < 8:
            return "menor"

        if len(password) > 32:
            return "maior"

        return {
            'sucesso': True,
            'password': password
        }

    @http.route(['/confirm-password/validate'], type='json', auth="public", methods=['POST'], csrf=False)
    def confirm_password_validate(self, **kwargs):
        password = kwargs['password']
        confirm_password = kwargs['confirm_password']

        if len(confirm_password) < 8:
            return "menor"

        if len(confirm_password) > 32:
            return "maior"

        if confirm_password != password:
            return "diferente"

        return True

    @http.route(['/reseller/validate'], type='json', auth="public", methods=['POST'], csrf=False)
    def resseler_validate(self, **kwargs):
        reseller_ids = kwargs['reseller_ids']
        if '/' in kwargs['date_schedule']:
            date_schedule = '%s-%s-%s' % (kwargs['date_schedule'][-4:],kwargs['date_schedule'][3:5],kwargs['date_schedule'][:-8])
        else:
            date_schedule = kwargs['date_schedule']

        desabilitar = {}

        cont_morning = 0
        cont_afternoon = 0
        cont_night = 0

        src_reseller = http.request.env['res.partner'].sudo().search([('resale','=',True),('id','=',int(reseller_ids))])

        qty_reseller = src_reseller.qty_installers * 2

        src_inst_sch = http.request.env['installation.schedule'].sudo().search([('date_scheduler','=',date_schedule),('reseller_id','=',src_reseller.id),('state','=','confirmed')])

        for installation in src_inst_sch:
            if installation.period == 'morning':
                cont_morning += 1

            if installation.period == 'afternoon':
                cont_afternoon += 1

            if installation.period == 'night':
                cont_night += 1

        if cont_morning >= qty_reseller:
            desabilitar.update({'morning': True})
        if cont_afternoon >= qty_reseller:
            desabilitar.update({'afternoon': True})
        if cont_night >= qty_reseller:
            desabilitar.update({'night': True})

        if desabilitar:
            return {'desabilitar': desabilitar}
        else:
            return {'desabilitar': {}}


    @http.route(['/number/validate'], type='json', auth="public", methods=['POST'], csrf=False)
    def card_number_validate(self, **kwargs):
        card_number = kwargs['card_number']

        for char in card_number:
            try:
                int(char)
            except:
                return "letras"

        if len(card_number) < 16:
            return "menor"

        return {
            'sucesso': True,
            'card_number': card_number,
        }

    @http.route(['/name/validate'], type='json', auth="public", methods=['POST'], csrf=False)
    def card_name_validate(self, **kwargs):
        name = kwargs['name']

        for char in name:
            if not char.isalpha():
                return "letras"

        if len(name) > 40:
            return "menor"

        return {
            'sucesso': True,
            'name': name,
        }

    @http.route(['/year/validate'], type='json', auth="public", methods=['POST'], csrf=False)
    def card_year_validate(self, **kwargs):
        year = kwargs['year']

        year_now = datetime.now().year

        if int(year) < year_now:
            return "vencido"

        for char in year:
            try:
                int(char)
            except:
                return "letras"

        if len(year) < 4:
            return "menor"

        return {
            'sucesso': True,
            'year': year,
        }

    @http.route(['/month/validate'], type='json', auth="public", methods=['POST'], csrf=False)
    def card_month_validate(self, **kwargs):
        month = kwargs['month']

        for char in month:
            try:
                int(char)
            except:
                return "letras"

        if int(month) < 0 or int(month) > 12:
            return "range"
        else:
            if len(month) == 1:
                month = "0" + month
            elif not int(month) <= 12:
                return "menor"

        return {
            'sucesso': True,
            'month': month,
        }

    @http.route(['/placa/validate'], type='json', auth="public", methods=['POST'], csrf=False)
    def plate_validate(self, **kwargs):
        placa = kwargs['placa']
        plate_upper = placa.upper()
        plate_upper_hifen = plate_upper[:3] + "-" + plate_upper[3:7]

        val = re.sub('[^A-Z0-9]', '', plate_upper)

        if not len(val) == 7:
            return "tamanho"

        for char in val[0:3]:
            if not char.isalpha():
                return "letras"

        for number in val[3:]:
            try:
                int(number)
            except:
                return "num"

        src_placa = http.request.env['vehicle.partner'].sudo().search(
            [('plate', 'in', [placa, plate_upper_hifen, kwargs['placa']])])

        if src_placa:
            return "erro"
        else:
            format_plate = val[0:3] + '-' + val[3:]
            return {'sucesso': True,
                    'placa': format_plate
                    }

    @http.route(['/page/next/scheduler'], type='http', auth="user", website=True)
    def next_pay(self, **kw):

        order = request.website.sale_get_order()

        type_installation = http.request.env['installation.schedule.type'].sudo().search([('type','=','inst')])

        vals = {
            'name': http.request.env['ir.sequence'].sudo().next_by_code('installation.schedule') or 'New',
            'partner_id': request.env['res.users'].sudo().browse(request.env.context['uid']).partner_id.id,
            'sale_order_id': order.id,
            'type_id': type_installation.id
        }

        http.request.env['installation.schedule'].sudo().create(vals)

        return request.redirect("/page/agendamento_instalacao")


class ApiController(Controller):

    @http.route(['/email/return'], type='http', auth='none', csrf=False)
    def confirm_quick_sale(self, quick_order):
        quick_sale = http.request.env['quick.sale'].sudo().search([('id','=',int(quick_order))])
        if quick_sale:
            # try:
            qsale = quick_sale.quick_sale_process_auto()
            if not 'state' in qsale:
                inv = http.request.env['account.invoice'].sudo().search([('sale_id','=',qsale['sale_id'])])[0]
                request_php = http.request.env['request.php'].sudo().firt_payment(inv, quick_sale)
                if request_php:
                    return 'Aprovado com Sucesso!'
                else:
                    #quick_sale.write({'state':'payment_error'})
                    return 'Por favor, entra em contato com o Vendedor, Problema no pagamento!'
            else:
                if qsale['state'] == 'payment_error':
                    return 'Por favor, entra em contato com o Vendedor, Problema no pagamento!'
                elif qsale['state'] == 'paid':
                    return u'Venda já Aprovado. Obrigado!'
                else:
                    return 'Por favor, entra em contato com o Vendedor!'
            # except:
            #     return 'Por favor, entra em contato com o Vendedor!'


    @http.route(['/api/email/return/sale'], type='http', auth='none', csrf=False)
    def confirm_sale(self, sale_order):
        sale = http.request.env['sale.order'].sudo().search([('id','=',int(sale_order))])

        if sale:
            sale.action_confirm()
            sale.action_invoice_create()
            inv = http.request.env['account.invoice'].sudo().search([('sale_id','=',sale.id)])[0]
            request_php = http.request.env['request.php'].sudo().firt_payment(inv)
            if request_php:
                return 'Aprovado com Sucesso!'
            else:
                return 'Por favor, entra em contato com o Vendedor!'

class WebsiteSaleFormTracknem(WebsiteForm):

    @http.route(['/shop/payment/transaction/<int:acquirer_id>'], type='json', auth="public", website=True)
    def payment_transaction(self, acquirer_id, tx_type='form', token=None, **kwargs):
        """ Json method that creates a payment.transaction, used to create a
        transaction when the user clicks on 'pay now' button. After having
        created the transaction, the event continues and the user is redirected
        to the acquirer website.

        :param int acquirer_id: id of a payment.acquirer record. If not set the
                                user is redirected to the checkout page
        """
        user = request.env['res.users'].sudo().browse(request.env.context['uid'])
        part = user.partner_id
        if not 'installment' in kwargs:
            return False
        if part:
            sale = request.website.sale_get_order()
            amount = sale.amount_total#request.env['payment.transaction'].sudo().browse(acquirer_id).amount
            dict_payment = {
                "user": 0,
                "buyerName": part.name,
                "buyerDocumentType": "CPF",
                "buyerDocumentNumber": part.cnpj_cpf,
                "buyerType": "Person",
                "transactionOperation": user.company_id.type_transition, # "AuthOnly",  #AuthOnly //AuthAndCapture //mudar para AuthAndCapture
                "transactionPrice": amount,
                'creditCardHolderName': part.credit_card_name,
                'creditCardBrand': part.credit_card_payment_acquirer.name,
                'creditCardNumber': part.credit_card_number,
                'creditCardSecurityCode': part.credit_card_security_code,
                'creditCardExpMonth': part.credit_card_month_expiration,
                'creditCardExpYear': part.credit_card_year_expiration,
                "transactionInstallmentCount": int(kwargs['installment'])
            }
            # dict_payment = {
            #     'password': user.login, #TODO PASSWORD CRYPT
            #     'confirmPassword': user.login, #TODO PASSWORD CRYPT
            #     'partnerId': part.id,
            #     'gender': part.gender or 'MALE',
            #     'birthDate': part.birthdate or ,
            #     'orderId': acquirer_id,
            #     'name': part.name,
            #     'email': part.email,
            #     'cpfCnpj': part.cnpj_cpf,
            #     'value': amount,
            #     'creditCardHolderName': part.credit_card_name,
            #     'creditCardBrand': part.credit_card_payment_acquirer.name,
            #     'creditCardNumber': part.credit_card_number,
            #     'creditCardSecurityCode': part.credit_card_security_code,
            #     'creditCardExpMonth': part.credit_card_month_expiration,
            #     'creditCardExpYear': part.credit_card_year_expiration
            #   }
            #url = "http://localhost/api/cc-payment/php-rest.php"
            #response = req.post(url, dict_payment)
            headers = {"Content-Type": "application/json", "Accept": "application/json"}
            url_payment = "https://www.telefonicarastreamento.com.br/api/credit-card/approve/"
            json_payment = json.dumps(dict_payment)
            response = req.post(url_payment, data=json_payment, headers=headers)
            if response.status_code == 201:
                resp = response.json()
                #if 'partner' in resp:


                vehicle_website = request.env['vehicle.partner.website'].sudo().search(
                    [('partner_id', '=', sale.partner_id.id), ('state', '=', 'draft')])
                if sale.state == 'draft':
                    sale.sudo().action_confirm()
                if sale.invoice_status == 'to invoice':
                    sale.sudo().action_invoice_create()
                inv = sale.env['account.invoice'].sudo().search([('sale_id', '=', sale.id)])[0]
                if inv.state == 'draft':
                    inv.action_invoice_open()
                cnpj_cpf = re.sub("[^0-9]", "", part.cnpj_cpf)

                part.sudo().write({
                                  "instantBuyKey":eval(response.text)["instantBuyKey"]
                                     })

                dict_user = {
                    "user": {
                        "login" : part.email,
                        "name" : part.name,
                        "password" : part.password or user.password, #A senha deve conter entre 8 e 32 caracteres.
                        "confirmPassword" : part.password or user.password, #A senha deve conter entre 8 e 32 caracteres.
                        "cpfCnpj" : cnpj_cpf, #O CPF/CNPJ informado não corresponde a um CPF/CNPJ válido. Informe apenas os números sem barras, pontos ou hífens
                        "email" : part.email,
                        "gender" : part.gender or 'MALE',
                        "birthDate" : "%sT00:00:00" % (part.birthdate or date.today()),
                        "brand": "6713276314419200"
                            },
                    "origin": 'ERP'
                    }

                url_user = "https://www.telefonicarastreamento.com.br/api/signin/"
                json_user = json.dumps(dict_user)
                user_p = req.post(url_user, data=json_user, headers=headers)
                if user_p.status_code not in [200,201]:
                    http.request.env["account.invoice.log"].sudo().create({"log":u"Problema com Usuario - %s" % normalize('NFKD', eval(user_p.text)['message'].decode('utf-8')).encode('ASCII','ignore'), "invoice_id":inv.id})
                    return False
                else:
                    http.request.env["account.invoice.log"].sudo().create({"log":u"Cadastra de Usuario com Sucesso","invoice_id": inv.id})
                    if part:
                        part.sudo().write({
                                          "user_plataforma": str(eval(user_p.text)["user"]["id"])
                                             })
                for due in inv.receivable_move_line_ids:
                    journal = http.request.env['account.journal'].sudo().search([('code', '=', 'card')])
                    inv.pay_and_reconcile(journal, inv.amount_total, date.today(), None)
                    http.request.env['account.invoice.log'].sudo().create(
                        {'log': u"Pagamento Efetuado com sucesso! - Com cartao %s OrderKey:(%s) - transactionKey:(%s)" % (eval(response.text)['creditCardMaskedNumber'],eval(response.text)["orderKey"],eval(response.text)["transactionKey"]), 'invoice_id': inv.id})

                    part.sudo().write({'credit_card_name':'',
                                'credit_card_number':'',
                                'credit_card_security_code':'',
                                'credit_card_month_expiration':'',
                                'credit_card_year_expiration':''})
                    # else:
                    #     self.env['account.invoice.log'].create(
                    #         {'log': u'Pagamento não Efetuado! - %s' % response, 'invoice_id': inv.id})

                value = {
                    'partner_id': sale.partner_id.id,
                    'pricelist_id': sale.pricelist_id.id,
                    'template_id': vehicle_website[0].plan_id.template_subscription_id.id or 1,
                    'company_id': sale.company_id.id,
                }

                sale_subscription = http.request.env['sale.subscription'].sudo().create(value)
                if vehicle_website:
                    for vehicle in vehicle_website:
                        if vehicle.plan_id:
                            value_line = {
                                'name': vehicle.plan_id.name,
                                'product_id': vehicle.plan_id.id,
                                'uom_id': vehicle.plan_id.uom_id.id,
                                'price_subtotal': vehicle.plan_id.lst_price,
                                'price_unit': vehicle.plan_id.lst_price,
                                'analytic_account_id': sale_subscription.id,
                                'sold_quantity': 1,
                                'quantity': 1,
                            }
                            http.request.env['sale.subscription.line'].sudo().create(value_line)

                type_installation = http.request.env['installation.schedule.type'].sudo().search([('type','=','inst')])

                vals = {
                    'name': http.request.env['ir.sequence'].sudo().next_by_code('installation.schedule') or 'New',
                    'partner_id': sale.partner_id.id,
                    'sale_order_id': sale.id,
                    'contract_id': sale_subscription.id,
                    'type_id': type_installation.id
                }

                http.request.env['installation.schedule'].sudo().create(vals)

                Transaction = request.env['payment.transaction'].sudo()

                # In case the route is called directly from the JS (as done in Stripe payment method)
                so_id = kwargs.get('so_id')
                so_token = kwargs.get('so_token')
                if so_id and so_token:
                    order = request.env['sale.order'].sudo().search([('id', '=', so_id), ('access_token', '=', so_token)])
                elif so_id:
                    order = request.env['sale.order'].search([('id', '=', so_id)])
                else:
                    order = request.website.sale_get_order()
                if not order or not order.order_line or acquirer_id is None:
                    return request.redirect("/shop/checkout")

                assert order.partner_id.id != request.website.partner_id.id

                # find an already existing transaction
                tx = request.website.sale_get_transaction()
                if tx:
                    if tx.sale_order_id.id != order.id or tx.state in ['error', 'cancel'] or tx.acquirer_id.id != acquirer_id:
                        tx = False
                    elif token and tx.payment_token_id and token != tx.payment_token_id.id:
                        # new or distinct token
                        tx = False
                    elif tx.state == 'draft':  # button cliked but no more info -> rewrite on tx or create a new one ?
                        tx.write(dict(Transaction.on_change_partner_id(order.partner_id.id).get('value', {}), amount=order.amount_total, type=tx_type))
                if not tx:
                    tx_values = {
                        'acquirer_id': acquirer_id,
                        'type': tx_type,
                        'amount': order.amount_total,
                        'currency_id': order.pricelist_id.currency_id.id,
                        'partner_id': order.partner_id.id,
                        'partner_country_id': order.partner_id.country_id.id,
                        'reference': Transaction.get_next_reference(order.name),
                        'sale_order_id': order.id,
                        'state': 'authorized'
                    }
                    if token and request.env['payment.token'].sudo().browse(int(token)).partner_id == order.partner_id:
                        tx_values['payment_token_id'] = token

                    tx = Transaction.create(tx_values)
                    request.session['sale_transaction_id'] = tx.id

                # update quotation
                order.write({
                    'payment_acquirer_id': acquirer_id,
                    'payment_tx_id': request.session['sale_transaction_id']
                })
                if token:
                    return request.env.ref('website_sale.payment_token_form').render(dict(tx=tx), engine='ir.qweb')

                return tx.acquirer_id.with_context(submit_class='btn btn-primary', submit_txt=_('Pay Now')).sudo().render(
                    tx.reference,
                    order.amount_total,
                    order.pricelist_id.currency_id.id,
                    values={
                        'return_url': '/page/agendamento_instalacao',
                        'partner_id': order.partner_shipping_id.id or order.partner_invoice_id.id,
                        'billing_partner_id': order.partner_invoice_id.id,
                    },
                )
            else:
                return False


class WebsitePlanOption(http.Controller):
    @http.route(['/page/terms_render'], type='http', auth="public", website=True)
    def signup(self, **kwargs):
        data_site = request.env['data.site'].sudo().search([('active', '=', True)])

        return http.request.render('vehicle_service.remove_title_terms', {
            'data_site': data_site,
        })


    @http.route('/page/choose_plan', type='http', auth='public', website=True)
    def choose_plan_form(self, **kw):

        Category = http.request.env['vehicle.category']
        Manufacturer = http.request.env['vehicle.manufacturer']
        Year = http.request.env['vehicle.year']
        Model = http.request.env['vehicle.model']

        return http.request.render('vehicle_service.page_choose_plan',{
            'categ_ids': Category.sudo().search([]),
            'manufacturer_ids': Manufacturer.sudo().search([]),
            'year_ids': Year.sudo().search([]),
            'model_ids': Model.sudo().search([]),
        })

    @http.route('/shop/manufacturer', type='json', auth='none', methods=['POST'], website=True)
    def get_manufacturer_json(self, categ):
        if categ:
            category = request.env['vehicle.category'].sudo().search([('name','=',categ)])
            if category:
                manufacturers = []
                request.cr.execute('select * from vehicle_manufacturer_category_rel where vehicle_category_id = %s' % category.id)
                res = request.cr.dictfetchall()
                for line in res:
                    manufacturers.append(request.env['vehicle.manufacturer'].sudo().browse(line['vehicle_manufacturer_id']))
                return [(manufacturer.id, manufacturer.name) for manufacturer in manufacturers]
            return []
        return []

    @http.route('/shop/model', type='json', auth='none', methods=['POST'], website=True)
    def get_model_json(self, **kwargs):
        manufac = kwargs['manufac']
        categ = kwargs['categ']

        if manufac:
            categ_id = request.env['vehicle.category'].sudo().search([('name', '=', categ)])
            manufac_id = request.env['vehicle.manufacturer'].sudo().search([('id','=',int(manufac))])
            if manufac_id:
                list_models = []
                models_ids = request.env['vehicle.model'].sudo().search([('manufacturer_id','=',manufac_id.id),('category_id','=',categ_id.id)])
                for line in models_ids:
                    if line.plan_ids:
                        list_models.append(line)
                return [(modelo.id, modelo.name) for modelo in list_models]
            return []
        return []

    @http.route('/shop/year', type='json', auth='none', methods=['POST'], website=True)
    def get_year_json(self, modelo):
        if modelo:
            model_id = request.env['vehicle.model'].sudo().search([('id', '=', int(modelo))])
            if model_id:
                years = []
                request.cr.execute(
                    'select * from vehicle_model_vehicle_year_rel where vehicle_model_id = %s' % model_id.id)
                res = request.cr.dictfetchall()
                for line in res:
                    years.append(
                        request.env['vehicle.year'].sudo().browse(line['vehicle_year_id']))
                return sorted([(year.id, year.name) for year in years])
            return []
        return []

    @http.route(['/shop/search_plan'], type='http', auth="public",
                methods=['POST'], website=True, csrf=False)
    def search_plans_json(self, **kwargs):
        category = kwargs['categ_id']
        model = kwargs['model_id']
        year = kwargs['year_id']
        manufacturer = kwargs['manufacturer_id']

        category = request.env['vehicle.category'].sudo().search([('name','=',category)])
        year = request.env['vehicle.year'].sudo().search([('id','=',year)])
        manufacturer = request.env['vehicle.manufacturer'].sudo().search([('id','=',manufacturer)])
        model = request.env['vehicle.model'].sudo().search([('id', '=', int(model))])

        products = []
        model_partner = {
            'categ': category.id,
            'model_id': model.id,
            'year': year.id,
            'manufacturer': manufacturer.id
        }
        for line in model.year_ids:
            if line.id == year.id:
                if model.product_id and model.plan_ids:
                    product_id = model.product_id
                    plan_ids = model.plan_ids
                    if product_id.website_published == False:
                        product_id.sudo().write({'website_published': True})
                    products.append(product_id.id)
                    for plans in plan_ids:
                        if plans.website_published == False:
                            plans.sudo().write({'website_published': True})
                        products.append(plans.id)
                    return http.request.redirect("/shop?search=plan-%s?vehicle=%s" % (products,model_partner))
                else:
                    raise UserError(_("O seu modelo carro não possui plano ou instalação disponíveis."))

        # if available_year != True:
        #     raise UserError(_("Infelizmente não realizamos instalação para este modelo de carro do ano informado."))

    @http.route(['/shop/edit_credit_card'], type='http', auth="public",
                methods=['GET'], website=True, csrf=False)
    def edit_credit_card(self, **kwargs):
        user_email = request.env['res.users'].browse(request.session.uid)

        if user_email:
            return http.request.render('vehicle_service.credit_card_register', {
                'partner_id': user_email.partner_id,
            })
        else:
            return http.request.render('vehicle_service.credit_card_register', {
                'partner_id': [],
            })

    @http.route(['/shop/edit_credit_card_portal'], type='http', auth="public",
                methods=['GET'], website=True, csrf=False)
    def edit_credit_card_portal(self, **kwargs):
        user_email = request.env['res.users'].browse(request.session.uid)

        if user_email:
            return http.request.render('vehicle_service.credit_card_register_portal', {
                'partner_id': user_email.partner_id,
            })
        else:
            return http.request.render('vehicle_service.credit_card_register_portal', {
                'partner_id': [],
            })


    @http.route(['/shop/credit_card_register'], type='http', auth="public",
                methods=['GET'], website=True, csrf=False)
    def credit_card_register_json(self, **kwargs):
        user_email = request.env['res.users'].browse(request.session.uid)

        if user_email:
            return http.request.render('vehicle_service.credit_card_register', {
                'partner_id': user_email.partner_id,
            })
        else:
            return http.request.render('vehicle_service.credit_card_register', {
                'partner_id': [],
            })

    @http.route(['/shop/credit-card'], type='http', auth="public",
                methods=['POST'], website=True, csrf=False)
    def credit_card_register_json2(self, **kwargs):
        card_flag = kwargs['credit_card_payment_acquirer']
        card_name = kwargs['credit_card_name']
        card_number = kwargs['credit_card_display_number']
        card_security = kwargs['credit_card_security_code']
        card_month = kwargs['credit_card_month_expiration']
        card_year = kwargs['credit_card_year_expiration']

        order = request.website.sale_get_order()

        if card_flag == 'mastercard':
            card_flag = 'Mastercard'
        elif card_flag == 'visa':
            card_flag = 'Visa'
        elif card_flag == 'amex':
            card_flag = 'American Express'
        else:
            card_flag = 'Elo'

        card_flag = request.env['payment.acquirer'].sudo().search([('name','=',card_flag)])
        if len(card_flag) > 1:
            card_flag = card_flag[0]
        user = request.env['res.users'].sudo().browse(request.env.context['uid']).partner_id

        vals = {
            'credit_card_payment_acquirer': card_flag.id,
            'credit_card_name': card_name,
            'credit_card_display_number': card_number,
            'credit_card_number': card_number,
            'credit_card_security_code': card_security,
            'credit_card_month_expiration': int(card_month),
            'credit_card_year_expiration': int(card_year),
        }

        user.sudo().write(vals)
        if order:
            return http.request.redirect("/shop/confirm_order")
        else:
            return http.request.redirect("/my/home")

    @http.route('/page/search_reseller', type='json', auth='none', methods=['POST'], website=True)
    def get_reseller_json(self, **kwargs):
        address = kwargs['address']
        if address:
            user = request.env['res.users'].sudo().browse(1)
            url = user.company_id.url_api_googlemaps
            radius = user.company_id.radius_search
            res = []
            cont = 0
            origin = address
            destination = ''
            for d in request.env['res.partner'].sudo().search([('resale','=',True)]):
                if d.zip:
                    destination = destination + d.zip + '|'
            url_search = url.replace('@origin',origin).replace('@dest',destination)
            try:
                google_search = req.get(url_search)
            except:
                return {'domain':{'reseller_id':[('id','in',res)]},'warning':'Erro de Conexão!'}
            result = google_search.json()
            cont_result = len(result['destination_addresses'])
            dest_list = destination.split('|')
            while cont < cont_result:
                if result['rows'][0]['elements'][cont]['status'] == 'OK' and \
                                result['rows'][0]['elements'][cont]['distance']['value'] < radius:
                    resales = request.env['res.partner'].sudo().search([('resale','=',True),('zip','=',dest_list[cont])])
                    res.append(resales)
                cont += 1
            if not res:
                return []
            else:
                return [(reseller.id, reseller.name + '(' + reseller.street + ' ' + reseller.number + ' ' + reseller.district + ' ' + reseller.city_id.name + ')') for reseller in res]
        return []

    @http.route('/page/schedule_service', type='http', auth='public', website=True)
    def schedule_service(self, **kw):
        request.session.authenticate(request.session.db, request.session.login, request.session.password)

        part = request.env['res.users'].sudo().browse(request.env.context['uid']).partner_id
        scheduler = request.env['installation.schedule'].sudo().search([('partner_id','=',part.id)])

        return request.render('vehicle_service.schedule_service', {
            'scheduler': scheduler,
        })


class WebsiteSaleInherit(WebsiteSale):

    @http.route(['/shop/product/<model("product.template"):product>'], type='http', auth="public", website=True)
    def product(self, product, category='', search='', **kwargs):
        mod = ''

        if not request.session.login:
            return http.request.redirect("/web/login?redirect=/shop/product/%s?search=%s" % (product.id,search))
        else:
            if 'plan-' in search:
                user_email = request.env['res.users'].browse(request.session.uid)
                vehicle_website = request.env['vehicle.partner.website'].sudo().search([('partner_id','=',user_email.partner_id.id),('state','=','draft')])
                model_vehicle = search.split("vehicle=")
                dmodel = eval(model_vehicle[1])
                mod = http.request.env['vehicle.model'].sudo().browse(dmodel['model_id'])
                dict_vehicle_website = {
                    'partner_id': user_email.partner_id.id,
                    'category_id': dmodel['categ'],
                    'manufacturer_id': dmodel['manufacturer'],
                    'model_id': dmodel['model_id'],
                    'plan_id': product.id,
                    'state': 'draft',
                    'year_id': dmodel['year']
                }
                if vehicle_website:
                    vehicle_website.sudo().write(dict_vehicle_website)
                else:
                    request.env['vehicle.partner.website'].sudo().create(dict_vehicle_website)
            product_context = dict(request.env.context, active_id=product.id)
            ProductCategory = request.env['product.public.category']
            Rating = request.env['rating.rating']

            if category:
                category = ProductCategory.browse(int(category)).exists()

            attrib_list = request.httprequest.args.getlist('attrib')
            attrib_values = [map(int, v.split("-")) for v in attrib_list if v]
            attrib_set = set([v[1] for v in attrib_values])

            keep = QueryURL('/shop', category=category and category.id, search=search, attrib=attrib_list)

            categs = ProductCategory.search([('parent_id', '=', False)])

            pricelist = request.website.get_current_pricelist()

            from_currency = request.env.user.company_id.currency_id
            to_currency = pricelist.currency_id
            compute_currency = lambda price: from_currency.compute(price, to_currency)

            # get the rating attached to a mail.message, and the rating stats of the product
            ratings = Rating.search([('message_id', 'in', product.website_message_ids.ids)])
            rating_message_values = dict([(record.message_id.id, record.rating) for record in ratings])
            rating_product = product.rating_get_stats([('website_published', '=', True)])

            if not product_context.get('pricelist'):
               product_context['pricelist'] = pricelist.id
               product = product.with_context(product_context)

            values = {
                'search': search,
                'category': category,
                'pricelist': pricelist,
                'attrib_values': attrib_values,
                'compute_currency': compute_currency,
                'attrib_set': attrib_set,
                'keep': keep,
                'categories': categs,
                'main_object': product,
                'product': product,
                'get_attribute_value_ids': self.get_attribute_value_ids,
                'rating_message_values': rating_message_values,
                'rating_product': rating_product,
            }

            if mod:
                values.update({'price_instalation': str('%.2f' % mod.product_id.list_price).replace('.', ',')})
            else:
                return http.request.redirect("/page/choose_plan")

            return request.render("website_sale.product", values)

    @http.route([
        '/shop',
        '/shop/page/<int:page>',
        '/shop/category/<model("product.public.category"):category>',
        '/shop/category/<model("product.public.category"):category>/page/<int:page>'
    ], type='http', auth="public", website=True)
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        mod = ''

        if ppg:
            try:
                ppg = int(ppg)
            except ValueError:
                ppg = PPG
            post["ppg"] = ppg
        else:
            ppg = PPG

        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [map(int, v.split("-")) for v in attrib_list if v]
        attributes_ids = set([v[0] for v in attrib_values])
        attrib_set = set([v[1] for v in attrib_values])

        # if search
        domain = self._get_search_domain(search, category, attrib_values)

        keep = QueryURL('/shop', category=category and int(category), search=search, attrib=attrib_list,
                        order=post.get('order'))
        pricelist_context = dict(request.env.context)
        if not pricelist_context.get('pricelist'):
            pricelist = request.website.get_current_pricelist()
            pricelist_context['pricelist'] = pricelist.id
        else:
            pricelist = request.env['product.pricelist'].browse(pricelist_context['pricelist'])

        request.context = dict(request.context, pricelist=pricelist.id, partner=request.env.user.partner_id)

        url = "/shop"
        if search:
            post["search"] = search
        if category:
            category = request.env['product.public.category'].browse(int(category))
            url = "/shop/category/%s" % slug(category)
        if attrib_list:
            post['attrib'] = attrib_list

        categs = request.env['product.public.category'].search([('parent_id', '=', False)])
        Product = request.env['product.template']

        parent_category_ids = []
        if category:
            parent_category_ids = [category.id]
            current_category = category
            while current_category.parent_id:
                parent_category_ids.append(current_category.parent_id.id)
                current_category = current_category.parent_id

        product_count = Product.search_count(domain)
        pager = request.website.pager(url=url, total=product_count, page=page, step=ppg, scope=7, url_args=post)

        if "plan-" in search:
            plan = search.split("vehicle=")
            mod = http.request.env["vehicle.model"].sudo().browse(eval(plan[1])['model_id'])
            products_list = plan[0].split("-")[1].split("[")[1].split("]")[0].split(",")
            list = []
            for line in products_list:
                list.append(int(line))
            products = Product.search([("id","in",list)], limit=ppg, offset=pager['offset'], order=self._get_search_order(post))
            #search = ''
        else:
            products = Product.search(domain, limit=ppg, offset=pager['offset'], order=self._get_search_order(post))

        ProductAttribute = request.env['product.attribute']
        if products:
            attributes = ProductAttribute.search([('attribute_line_ids.product_tmpl_id', 'in', products.ids)])
        else:
            attributes = ProductAttribute.browse(attributes_ids)

        from_currency = request.env.user.company_id.currency_id
        to_currency = pricelist.currency_id
        compute_currency = lambda price: from_currency.compute(price, to_currency)

        values = {
            'search': search,
            'category': category,
            'attrib_values': attrib_values,
            'attrib_set': attrib_set,
            'pager': pager,
            'pricelist': pricelist,
            'products': products,
            'search_count': product_count,  # common for all searchbox
            'bins': TableCompute().process(products, ppg),
            'rows': PPR,
            'categories': categs,
            'attributes': attributes,
            'compute_currency': compute_currency,
            'keep': keep,
            'parent_category_ids': parent_category_ids,
        }

        if mod:
            values.update({'price_instalation': str('%.2f' % mod.product_id.list_price).replace('.',',')})
        else:
            return http.request.redirect("/page/choose_plan")

        if category:
            values['main_object'] = category

        return request.render("website_sale.products", values)


    @http.route(['/shop/checkout'], type='http', auth="public", website=True)
    def checkout(self, **post):
        if not request.session.login:
            return http.request.redirect("/web/login?redirect=/shop/checkout")
        else:
            user_email = request.env['res.users'].browse(request.session.uid)
            order = request.website.sale_get_order()

            redirection = self.checkout_redirection(order)

            vehicle_website = request.env['vehicle.partner.website'].sudo().search([('partner_id', '=', user_email.partner_id.id), ('state', '=', 'draft')])
            if vehicle_website:
                price = vehicle_website[0].model_id.product_id.list_price
                for line in order.order_line:
                    line.write({'price_unit': price})
                if redirection:
                    return redirection

            if user_email.partner_id.id == request.website.user_id.sudo().partner_id.id:
                return request.redirect('/shop/address')

            for f in self._get_mandatory_billing_fields():
                if not order.partner_id[f]:
                    return request.redirect('/shop/address?partner_id=%d' % order.partner_id.id)

            values = self.checkout_values(**post)

            # Avoid useless rendering if called in ajax
            if post.get('xhr'):
                return 'ok'
            return request.render("website_sale.checkout", values)


    @http.route(['/shop/cart'], type='http', auth="public", website=True)
    def cart(self, **post):
        order = request.website.sale_get_order()
        user_email = request.env['res.users'].browse(request.session.uid)

        if order:
            from_currency = order.company_id.currency_id
            to_currency = order.pricelist_id.currency_id
            compute_currency = lambda price: from_currency.compute(price, to_currency)
        else:
            compute_currency = lambda price: price

        values = {
            'website_sale_order': order,
            'compute_currency': compute_currency,
            'suggested_products': [],
        }
        if order:
            _order = order
            if not request.env.context.get('pricelist'):
                _order = order.with_context(pricelist=order.pricelist_id.id)
            values['suggested_products'] = _order._cart_accessories()

        vehicle_website = request.env['vehicle.partner.website'].sudo().search([('partner_id', '=', user_email.partner_id.id), ('state', '=', 'draft')])
        if vehicle_website:
            price = vehicle_website[0].model_id.product_id.list_price
            for line in order.order_line:
                line.write({'price_unit': price})

        if post.get('type') == 'popover':
            return request.render("website_sale.cart_popover", values)

        if post.get('code_not_available'):
            values['code_not_available'] = post.get('code_not_available')

        return request.render("website_sale.cart", values)

    @http.route('/page/vehicle_register', type='http', auth='public', website=True)
    def vehicle_register_render(self, **kw):

        return http.request.render('vehicle_service.page_registro_veiculo')

    @http.route('/page/vehicle_register_submit', type='http', auth="public", methods=['POST'], website=True, csrf=False)
    def vehicle_submit(self, **kw):
        nome_proprietario = kw['nome_proprietario']
        placa = kw['placa']
        renavam = kw['renavam']


        user_email = request.env['res.users'].browse(request.session.uid)

        vehicle_website = request.env['vehicle.partner.website'].sudo().search(
            [('partner_id', '=', user_email.partner_id.id), ('state', '=', 'draft')])

        vals = {
            'plate': placa,
            'renavam': renavam,
            'owner_name': nome_proprietario,
        }

        vehicle_website.sudo().write(vals)

        return http.request.redirect('/shop/credit_card_register')

    @http.route('/page/agendamento_instalacao', type='http', auth='public', website=True)
    def schedule_installation(self, **kw):

        user_email = request.env['res.users'].browse(request.session.uid)

        vehicle_website = request.env['vehicle.partner.website'].sudo().search(
            [('partner_id', '=', user_email.partner_id.id), ('state', '=', 'draft')])

        reseller_ids = http.request.env['res.partner'].sudo().search([('resale','=',True)])

        return http.request.render('vehicle_service.page_agendamento_instalacao', {
                'reseller_ids': reseller_ids,
                'vehicle_website': vehicle_website,
            })

    @http.route(['/shop/confirm_order'], type='http', auth="public", website=True)
    def confirm_order(self, **post):
        order = request.website.sale_get_order()

        redirection = self.checkout_redirection(order)
        if redirection:
            return redirection

        order.onchange_partner_shipping_id()
        order.order_line._compute_tax_id()
        request.session['sale_last_order_id'] = order.id
        request.website.sale_get_order(update_pricelist=True)
        extra_step = request.env.ref('website_sale.extra_info_option')
        if extra_step.active:
            return request.redirect("/shop/extra_info")
        user_email = request.env['res.users'].browse(request.session.uid)
        vehicle_website = request.env['vehicle.partner.website'].sudo().search([('partner_id', '=', user_email.partner_id.id), ('state', '=', 'draft')])
        price = vehicle_website[0].model_id.product_id.list_price
        for line in order.order_line:
            line.write({'price_unit': price})
        return request.redirect("/shop/payment")

    @http.route(['/shop/confirm-schedule'], type='http', auth="public", methods=['POST'], website=True, csrf=False)
    def confirm_schedule(self, **kwargs):
        reseller = kwargs['reseller_ids']
        date = kwargs['date_schedule']
        periodo = kwargs['optradio']

        order = request.website.sale_get_order()

        if not order:
            order = request.session.sale_order_id
            order = http.request.env['sale.order'].sudo().browse(order)
            if not order:
                raise UserError(_('Nenhum CEP encontrado'))

        scheduler_ids = http.request.env['installation.schedule'].sudo().search([('sale_order_id','=',order.id),('state','=','draft')])
        reseller_id = http.request.env['res.partner'].sudo().search([('id','=',reseller),('resale','=',True)])


        if periodo == 'dia':
            periodo = 'morning'

        if periodo == 'tarde':
            periodo = 'afternoon'

        if periodo == 'noite':
            periodo = 'night'



        user_email = request.env['res.users'].browse(request.session.uid)
        vehicle_website = request.env['vehicle.partner.website'].sudo().search([('partner_id', '=', user_email.partner_id.id), ('state', '=', 'draft')])

        vehicle_partner = request.env['vehicle.partner'].sudo().create({
            'plate': vehicle_website.plate,
            'renavam': vehicle_website.renavam,
            'owner_name': vehicle_website.owner_name,
            'partner_id': user_email.partner_id.id,
            'year_id': vehicle_website.year_id.id,
            'model_id': vehicle_website.model_id.id,
            'category_id': vehicle_website.category_id.id,
            'manufacturer_id': vehicle_website.manufacturer_id.id
        })

        vals = {
            'reseller_id': reseller_id.id,
            'date_scheduler': '%s-%s-%s' % (date[6:],date[3:-5],date[:-8]),
            'period': periodo,
            'vehicle_id': vehicle_partner.id,
            'state': 'confirmed',
        }
        _logger.info('%s' % str(vals))
        for scheduler in scheduler_ids:
            scheduler.sudo().write(vals)

        request.session['sale_last_order_id'] = order.id
        tx = request.website.sale_get_transaction()

        return http.request.redirect("/shop/payment/validate?trasaction_id=%s?sale_order_id=%s" % (tx.id,order.id))

    @http.route('/shop/payment/get_status/<int:sale_order_id>', type='json', auth="public", website=True)
    def payment_get_status(self, sale_order_id, **post):
        order = request.env['sale.order'].sudo().browse(sale_order_id)
        assert order.id == request.session.get('sale_last_order_id')

        values = {}
        flag = False
        if not order:
            values.update({'not_order': True, 'state': 'error'})
        else:
            tx = request.env['payment.transaction'].sudo().search(
                ['|', ('sale_order_id', '=', order.id), ('reference', '=', order.name)], limit=1
            )

            if not tx:
                if order.amount_total:
                    values.update({'tx_ids': False, 'state': 'error'})
                else:
                    values.update({'tx_ids': False, 'state': 'done', 'validation': None})
            else:
                state = 'authorized'#tx.state
                flag = state == 'pending'
                values.update({
                    'tx_ids': True,
                    'state': state,
                    'acquirer_id': tx.acquirer_id,
                    'validation': tx.acquirer_id.auto_confirm == 'none',
                    'tx_post_msg': tx.acquirer_id.post_msg or None
                })

        return {'recall': flag,
                'message': request.env['ir.ui.view'].render_template("website_sale.order_state_message", values)}
