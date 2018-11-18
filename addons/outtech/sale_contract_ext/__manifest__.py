# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'Subscription Management (without frontend)',
    'version': '1.1',
    'category': 'Sales',
    'description': """
This module allows you to manage subscriptions.
Features:
    - Create & edit subscriptions
    - Modify subscriptions with sales orders
    - Generate invoice automatically at fixed intervals
""",
    'author': 'Outtech',
    'depends': ['sale_contract','website_contract','br_account'],
    'data': [
        'views/sale_subscription_template.xml'

    ],
    'license': 'OEEL-1',
    'installable': True,
}
