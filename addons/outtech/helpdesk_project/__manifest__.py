# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

{
    "name": "Helpdesk Project Integration",
    "version": "10.0.2",
    "author": "Bizzappdev",
    "website": "http://www.bizzappdev.com",
    "category": "Helpdesk",
    "depends": ["base", "helpdesk", "project", "hr_timesheet", "account"],
    "summary": "Project Helpdesk Integration",
    "description": """
    Track leads, close opportunities and get accurate forecasts.
    """,
    'images': [],
    "init_xml": [],
    "data": [
        'security/ir.model.access.csv',
        'views/helpdesk_team_view.xml',
        'views/helpdesk_view.xml',
    ],
    'demo_xml': [
    ],
    'price': 99,
    'currency': 'EUR',
    'test': [
    ],
    'installable': True,
    'active': False,
    'auto_install': False,
    'application': False,
    'images': ['images/1support_odoo.png'],
    'license': 'Other proprietary',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
