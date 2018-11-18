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
    'name': 'Point of Sale Extension',
    'version': '001.01',
    'author': 'Outtech',
    'maintainer': 'Outtech',
    'website': 'http://www.outtech.com.br/',
    'category': 'Point Of Sale',
    'sequence': 20,
    'summary': 'Point of Sale Extension',
    'description': """
Point of Sale Extension
===========================

This module extends the Point of Sale module to make some upgrades to it.
    """,
    'depends': ['base',
                'point_of_sale',
                'discount_permission',
                'br_point_sale',
                'file_import_export',
                'account',
                'product_ext'
                # 'hw_escpos',
                ],
    'data': [
        'views/pos_template.xml',
        'views/account_journal_view.xml',
        'views/account_view.xml',
        'views/point_of_sale_view.xml',
        'views/pos_order_view.xml',
        'views/res_users_view.xml',
        'views/res_company_view.xml',
        'views/res_holiday_view.xml',
        'views/res_partner_view.xml',
        'views/monthly_installments_view.xml',
        'views/discount_allowed_view.xml',
        'views/payment_validate_pos_view.xml',
        'views/account_bank_statement_view.xml',
        'report/pos_closing_report.xml',
        'report/pos_closing_report_templates.xml',
        'report/pos_discount_report.xml',
        'report/pos_discount_report_templates.xml',
        'report/pos_discount_report_ranking_templates.xml',
        'report/pos_amount_total.xml'
        #'views/2via_receipt_view.xml',
    ],

    'js': [
        'static/src/js/pos_ext.js',
           ],
    'installable': True,
    'application': True,
    'qweb': [
        'static/src/xml/pos.xml',
        'static/src/xml/cliente_pos.xml',
             ],
    'css': ['static/src/css/*.css'],
}
