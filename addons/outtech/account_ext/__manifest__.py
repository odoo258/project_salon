# -*- coding: utf-8 -*-
# © 2017 Jefferson Tito, Outtech
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Account Ext',
    'description': """Account""",
    'version': '11.0.1.0.0',
    'category': 'account',
    'author': 'Outtech',
    'license': 'AGPL-3',
    'website': 'http://www.outtech.com.br',
    'contributors': [
        'Jefferson Tito',
        'João Pedro Campos Silva'
    ],
    'depends': [
        'account', 'br_account', 'br_account_payment',
    ],
    'data': [
        'views/purchase_view.xml',
        'views/account_payment_view.xml',
    ],
}
