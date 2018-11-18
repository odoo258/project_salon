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

from odoo import api, models, fields, SUPERUSER_ID
import requests
from datetime import date
import logging
import re
import json
from unicodedata import normalize
_logger = logging.getLogger(__name__)

class RequestPhp(models.Model):
    _name = "request.php"

    def firt_payment(self, inv, quick_sale=False):
        if inv and inv.company_id.active_api:
            #Cria Header para requests
            headers = {"Content-Type": "application/json", "Accept": "application/json"}
            cnpj_cpf = re.sub("[^0-9]", "", inv.partner_id.cnpj_cpf)
            #Verifica status da Fatura e confirma se necessario
            if inv.state == "draft":
                inv.sudo().action_invoice_open()
            #Verifica se o usuario ja existe na plataforma
            if inv.partner_id.user_plataforma:
                return self.recurrency_payment(inv, quick_sale)
            #Tenta realizar o pagamento
            for due in inv.receivable_move_line_ids:
                # Pagamento na Plataforma
                try:
                    user = False
                    dict_payment = {
                        "user": 0,
                        "buyerName": inv.partner_id.name,
                        "buyerDocumentType":"CPF",
                        "buyerDocumentNumber": cnpj_cpf,
                        "buyerType": "Person",
                        "transactionOperation": inv.company_id.type_transition, #"AuthOnly",  #AuthOnly //AuthAndCapture //mudar para AuthAndCapture
                        "transactionPrice": due.debit,
                        "creditCardHolderName": inv.partner_id.credit_card_name,
                        "creditCardBrand": inv.partner_id.credit_card_payment_acquirer.name,
                        "creditCardNumber": inv.partner_id.credit_card_number,
                        "creditCardSecurityCode": inv.partner_id.credit_card_security_code,
                        "creditCardExpMonth": inv.partner_id.credit_card_month_expiration,
                        "creditCardExpYear": inv.partner_id.credit_card_year_expiration,
                        "transactionInstallmentCount": int(quick_sale.qty_plots)
                    }

                    url_payment = "%s/api/credit-card/approve/" % inv.company_id.url_api
                    json_payment = json.dumps(dict_payment)
                    payment = requests.post(url_payment, data=json_payment, headers=headers)

                    if payment.status_code not in [200,201]:
                        _logger.info('Payment erro - %s', normalize('NFKD', eval(payment.text)["message"].decode('utf-8')).encode('ASCII','ignore'))
                        if quick_sale:
                            self.env["account.invoice.log"].sudo().create({"log":u"Pagamento nao Efetuado! - %s" % normalize('NFKD', eval(payment.text)['message'].decode('utf-8')).encode('ASCII','ignore'),"invoice_id":inv.id, "quick_sale_id":quick_sale.id})
                            quick_sale.sudo().write({"state":"payment_error"})
                        else:
                            self.env["account.invoice.log"].sudo().create({"log":u"Pagamento nao Efetuado! - %s" % normalize('NFKD', eval(payment.text)['message'].decode('utf-8')).encode('ASCII','ignore'),"invoice_id":inv.id})
                        return False

                    else:
                        # _logger.info('Payment ok - %s', normalize('NFKD', eval(payment.text).decode('utf-8')).encode('ASCII','ignore'))
                        _logger.info('Payment ok')
                        journal = self.env["account.journal"].sudo().search([("code","=","card")])
                        inv.sudo().pay_and_reconcile(journal, inv.amount_total, date.today(), None)
                        if quick_sale:
                            self.env["account.invoice.log"].sudo().create({"log":u"Pagamento Efetuado com sucesso! - Com cartao %s OrderKey:(%s) - transactionKey:(%s)" % (eval(payment.text)['creditCardMaskedNumber'],eval(payment.text)["orderKey"],eval(payment.text)["transactionKey"]),"invoice_id":inv.id, "quick_sale_id":quick_sale.id})
                        inv.partner_id.sudo().write({"instantBuyKey":eval(payment.text)["instantBuyKey"],
                                                 "orderKey": eval(payment.text)["orderKey"],
                                                 "transactionKey": eval(payment.text)["transactionKey"],
                                                 'credit_card_name':'',
                                                 'credit_card_number':'',
                                                 'credit_card_security_code':'',
                                                 'credit_card_month_expiration':'',
                                                 'credit_card_year_expiration':''
                                                     })
                except Exception, m:
                    _logger.info('Payment Error - %s', m)
                    if not quick_sale:
                        self.env["account.invoice.log"].sudo().create({"log":u"Pagamento nao Efetuado! - %s" % m,"invoice_id":inv.id})
                    else:
                        self.env["account.invoice.log"].sudo().create({"log":u"Pagamento nao Efetuado! - %s" % m,"invoice_id":inv.id, "quick_sale_id":quick_sale.id})
                        quick_sale.sudo().write({"state":"payment_error"})

                if payment.status_code in [200,201]:
                    #Tenta criar cadastro de usuario na plataforma
                    try:
                        #Cadastro Plataforma
                        dict_user = {
                            "user": {
                                "login" : inv.partner_id.email,
                                "name" : inv.partner_id.name,
                                "password" : inv.partner_id.password, #A senha deve conter entre 8 e 32 caracteres.
                                "confirmPassword" : inv.partner_id.password, #A senha deve conter entre 8 e 32 caracteres.
                                "cpfCnpj" : cnpj_cpf, #O CPF/CNPJ informado não corresponde a um CPF/CNPJ válido. Informe apenas os números sem barras, pontos ou hífens
                                "email" : inv.partner_id.email,
                                "gender" : inv.partner_id.gender,
                                "birthDate" : "%sT00:00:00" % inv.partner_id.birthdate,
                                 "brand": "6713276314419200"
                                    },
                            "origin": 'ERP'
                            }


                        url_user = "%s/api/signin/" % inv.company_id.url_api
                        json_user = json.dumps(dict_user)
                        user = requests.post(url_user, data=json_user, headers=headers)
                        _logger.info('User - %s' % user.text)
                        if user.status_code not in [200,201]:
                            if not quick_sale:
                                self.env["account.invoice.log"].sudo().create({"log":u"Problema com Usuario - %s" % normalize('NFKD', eval(user.text)['message'].decode('utf-8')).encode('ASCII','ignore'),"invoice_id":inv.id})
                            else:
                                self.env["account.invoice.log"].sudo().create({"log":u"Problema com Usuario - %s" % normalize('NFKD', eval(user.text)['message'].decode('utf-8')).encode('ASCII','ignore'), "invoice_id":inv.id, "quick_sale_id":quick_sale.id})
                                quick_sale.sudo().write({"state":"user_error"})
                        else:
                            if quick_sale:
                                quick_sale.create_user()
                                self.env["account.invoice.log"].sudo().create({"log":u"Usuario cadastrado com sucesso","invoice_id":inv.id, "quick_sale_id":quick_sale.id})
                            else:
                                self.env["account.invoice.log"].sudo().create({"log":u"%s" % normalize('NFKD', eval(user.text)['message'].decode('utf-8')).encode('ASCII','ignore'),"invoice_id":inv.id})
                    except Exception, e:
                        if not quick_sale:
                            self.env["account.invoice.log"].sudo().create({"log":u"Problema com Usuario - %s" % e,"invoice_id":inv.id})
                        else:
                            self.env["account.invoice.log"].sudo().create({"log":u"Problema com Usuario - %s" % e, "invoice_id":inv.id, "quick_sale_id":quick_sale.id})
                            quick_sale.sudo().write({"state":"user_error"})
                #Se pagamento e usuario estiver ok Cria os logs
                if payment.status_code in [200,201] and user.status_code in [200,201]: # and register_card:
                    journal = self.env["account.journal"].sudo().search([("code","=","card")])
                    #inv.sudo().pay_and_reconcile(journal, inv.amount_total, date.today(), None)
                    if quick_sale:
                        self.env["account.invoice.log"].sudo().create({"log":u"Pagamento Efetuado com sucesso! - Com cartao %s OrderKey:(%s) - transactionKey:(%s)" % (eval(payment.text)['creditCardMaskedNumber'],eval(payment.text)["orderKey"],eval(payment.text)["transactionKey"]),"invoice_id":inv.id, "quick_sale_id":quick_sale.id})

                        quick_sale.sudo().write({"state":"paid",
                                                 'number_credit_card':''})
                    else:
                        self.env["account.invoice.log"].sudo().create({"log":u"Pagamento Efetuado com sucesso! - Com cartao %s OrderKey:(%s) - transactionKey:(%s)" % (eval(payment.text)['creditCardMaskedNumber'],eval(payment.text)["orderKey"],eval(payment.text)["transactionKey"]),"invoice_id":inv.id})
                    inv.partner_id.sudo().write({"instantBuyKey":eval(payment.text)["instantBuyKey"],
                                             "orderKey": eval(payment.text)["orderKey"],
                                             "transactionKey": eval(payment.text)["transactionKey"],
                                              "user_plataforma": str(eval(user.text)["user"]["id"]),
                                                 'credit_card_name':'',
                                                 'credit_card_number':'',
                                                 'credit_card_security_code':'',
                                                 'credit_card_month_expiration':'',
                                                 'credit_card_year_expiration':''
                                                 })
                    return True
                else:
                    #Verifica se o pagamento foi aprovado e o usuario nao cadastrado
                    if not user and payment.status_code in [200,201]:
                        if quick_sale:
                            if payment:
                                quick_sale.sudo().write({"state":"user_error"})
                                self.env["account.invoice.log"].sudo().create({"log":u"Pagamento Efetuado com sucesso! - Com cartao %s (Usuario nao cadastrado na plataforma) OrderKey:(%s) - transactionKey:(%s)" % (eval(payment.text)['creditCardMaskedNumber'],eval(payment.text)["orderKey"],eval(payment.text)["transactionKey"]),"invoice_id":inv.id, "quick_sale_id":quick_sale.id})
                            self.env["account.invoice.log"].sudo().create({"log":u"%s" % normalize('NFKD', eval(user.text)['message'].decode('utf-8')).encode('ASCII','ignore'),"invoice_id":inv.id, "quick_sale_id":quick_sale.id})
                        else:
                            self.env["account.invoice.log"].sudo().create({"log":u"%s" % normalize('NFKD', eval(user.text)['message'].decode('utf-8')).encode('ASCII','ignore'),"invoice_id":inv.id})
                        return False
                    #Pagamento com problema criar log
                    if payment.status_code not in [200,201]:
                        if quick_sale:
                            self.env["account.invoice.log"].sudo().create({"log":u"Pagamento nao Efetuado! - %s" % normalize('NFKD', eval(payment.text)['message'].decode('utf-8')).encode('ASCII','ignore'),"invoice_id":inv.id, "quick_sale_id":quick_sale.id})
                            quick_sale.sudo().write({"state":"payment_error"})
                        else:
                            self.env["account.invoice.log"].sudo().create({"log":u"Pagamento nao Efetuado! - %s" % normalize('NFKD', eval(payment.text)['message'].decode('utf-8')).encode('ASCII','ignore'),"invoice_id":inv.id})
                        return False


    def recurrency_payment(self, inv, quick_sale=False):
        if inv and inv.company_id.active_api:
            #Criacao de Header para request
            headers = {"Content-Type": "application/json", "Accept": "application/json"}
            #Verifica status de fatura e confirma se necessario
            if inv.state == "draft":
                inv.sudo().action_invoice_open()
            #Tenta fazer o pagamento recorrente
            for due in inv.receivable_move_line_ids:
                try:
                    dict_payment = {
                                'transactionOperation': inv.company_id.type_transition, #'AuthOnly',  #AuthOnly //AuthAndCapture //mudar para AuthAndCapture
                                'transactionPrice': due.debit,
                                'instantBuyKey': inv.partner_id.instantBuyKey#recurrencyKey
                                }
                    url_payment = "%s/api/credit-card/approve/" % inv.company_id.url_api
                    json_payment = json.dumps(dict_payment)
                    payment = requests.post(url_payment, data=json_payment, headers=headers)
                    if payment.status_code in [200,201]:
                        journal = self.env["account.journal"].sudo().search([("code","=","card")])
                        inv.sudo().pay_and_reconcile(journal, inv.amount_total, date.today(), None)
                        if quick_sale:
                            self.env["account.invoice.log"].sudo().create({"log":u"Pagamento Efetuado com sucesso! - Com cartao %s OrderKey:(%s) - transactionKey:(%s)" % (eval(payment.text)['creditCardMaskedNumber'],eval(payment.text)["orderKey"],eval(payment.text)["transactionKey"]),"invoice_id":inv.id, "quick_sale_id":quick_sale.id})
                            return quick_sale.sudo().write({"state":"paid",
                                                            'number_credit_card':''
                                                            })
                        else:
                            self.env["account.invoice.log"].sudo().create({"log":u"Pagamento Efetuado com sucesso! - Com cartao %s OrderKey:(%s) - transactionKey:(%s)" % (eval(payment.text)['creditCardMaskedNumber'],eval(payment.text)["orderKey"],eval(payment.text)["transactionKey"]),"invoice_id":inv.id})
                        return True
                    else:
                        if quick_sale:
                            self.env["account.invoice.log"].sudo().create({"log":u"Pagamento nao Efetuado! - %s" % normalize('NFKD', eval(payment.text)['message'].decode('utf-8')).encode('ASCII','ignore'),"invoice_id":inv.id})
                            return quick_sale.sudo().write({"state":"payment_error"})
                        else:
                            return self.env["account.invoice.log"].sudo().create({"log":u"Pagamento nao Efetuado! - %s" % normalize('NFKD', eval(payment.text)['message'].decode('utf-8')).encode('ASCII','ignore'),"invoice_id":inv.id})
                except Exception, m:
                   self.env["account.invoice.log"].sudo().create({"log":u"Pagamento nao Efetuado! - Problema no Cartao de Credito - %s" % m,"invoice_id":inv.id})
                   return False
        else:
            return False





