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

{
    'name': 'Bank Payment',
    'version': '001.01',
    'author': 'Outtech',
    'maintainer': 'Outtech',
    'website': 'http://www.outtech.com.br/',
    'category': 'account',
    'sequence': 30,
    'summary': 'Bank Payments',
    'description': """

        Bank Payments to bank transactions.

    """,
    'depends': [
            'base',
            'br_boleto',
            'file_import_export'
                ],
    'data': [
            'data/account_payment_method.xml',
            'views/account_invoice_view.xml',
            'views/bank_payment_view.xml',
            'views/lot_payment_view.xml',
            'views/bank_file_view.xml',
            'views/account_move_line_view.xml',
            'views/payment_mode_view.xml',
            'views/sequence.xml',
            'views/res_bank_view.xml',
            'wizard/bank_payment_create_view.xml',
            'wizard/lot_payment_create_view.xml',
            'wizard/export_cnab_view.xml',
            'wizard/export_pagfor_view.xml',
            'wizard/import_cnab_view.xml'
             ],
    'js': [],
    'installable': True,
    'application': False,
    'qweb': [],
}