# -*- coding: utf-8 -*-
# © 2016 Alessandro Fernandes Martini, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
import re

class ChangeCreditCard(models.TransientModel):
    _name = 'change.credit.card'

    name_credit_card = fields.Char(string="Name", required=True)
    number_credit_card = fields.Char(string="Number", required=True)
    credit_card_month_expiration = fields.Integer(string='Month Expiration', required=True)
    credit_card_year_expiration = fields.Integer(string='Year Expiration', required=True)
    security_code_credit_card = fields.Char(string="Security Code", size=3, required=True)
    payment_acquirer_credit_card = fields.Many2one('payment.acquirer', string="Flag", required=True)


    def confirm_change(self):
        quick_sale = self.env['quick.sale'].browse(self._context['active_id'])
        dict = {
            'name_credit_card': self.name_credit_card,
            'number_credit_card': self.number_credit_card,
            'credit_card_month_expiration': self.credit_card_month_expiration,
            'credit_card_year_expiration': self.credit_card_year_expiration,
            'security_code_credit_card': self.security_code_credit_card,
            'payment_acquirer_credit_card': self.payment_acquirer_credit_card.id,
            'display_number_credit_card': self.number_credit_card,
        }
        quick_sale.write(dict)
        if quick_sale.cnpj_cpf_partner:
            if quick_sale.is_company_partner:
                cnpj_cpf = re.sub('[^0-9]', '', quick_sale.cnpj_cpf_partner)
                if len(cnpj_cpf) == 14:
                    cnpj_cpf = '' + cnpj_cpf[:2] + '.' + cnpj_cpf[2:5] + '.' + cnpj_cpf[5:8] + '/' + cnpj_cpf[8:12] + '-' + cnpj_cpf[12:14]
                else:
                    return {'warning':{'title': _('Warning'), 'message': _('CNPJ do not have 14 characters.')}}
            else:
                cnpj_cpf = re.sub('[^0-9]', '', quick_sale.cnpj_cpf_partner)
                if len(cnpj_cpf) == 11:
                    cnpj_cpf = '' + cnpj_cpf[0:3] + '.' + cnpj_cpf[3:6] + '.' + cnpj_cpf[6:9] + '-' + cnpj_cpf[9:11]
                else:
                    return {'warning': {'title': _('Warning'), 'message': _('CPF do not have 11 characters.')}}

            res_partner_ids = self.env['res.partner'].search([('cnpj_cpf','=',cnpj_cpf)])

        dict_partner = {

            'credit_card_name': self.name_credit_card,
            'credit_card_number': self.number_credit_card,
            'credit_card_month_expiration': self.credit_card_month_expiration,
            'credit_card_year_expiration': self.credit_card_year_expiration,
            'credit_card_security_code': self.security_code_credit_card,
            'credit_card_payment_acquirer': self.payment_acquirer_credit_card.id
        }

        if res_partner_ids:
            res_partner_ids.write(dict_partner)
        return True

