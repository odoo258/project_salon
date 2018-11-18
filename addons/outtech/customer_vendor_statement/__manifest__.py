# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Customer Vendor Statement',
    'version': '1.0',
    'category': 'Accounting & Finance',
    'summary': 'Statement for customer and Vendor by currency',
    'description':'open any customer or vendor form and click on action--> Customer / Vendor Statement',
    "author": "Abdallah Mohamed - updated by Jôvani Moura",
    'website': 'abdalla_mohammed@outlook.com',
    'depends': [
        'account',
    ],
    'data': [
        'views/statement.xml',
        'views/menuitems.xml',
        'wizard/customer_vendor_statement_wizard.xml',
    ],
    'installable': True,
    'application': False,
}
