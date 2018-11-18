# -*- coding: utf-8 -*-
# © 2017 Outtech - http://www.outtech.com.br/
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Vehicle Service',
    'description': """Vehicle Service""",
    'category': 'Service',
    'author': 'Outtech',
    'maintainer': 'Outtech',
    'website': 'http://www.outtech.com.br/',
    'version': '001.01',
    'depends': [
        'base',
        'br_base',
        'sale',
        'sale_contract',
        'delivery',
        'website',
        'website_portal',
        'website_sale_options',
        'website_project_issue',
        'website_legal_page'
    ],

    'js': [
        'static/src/js/device-control.js',
        'static/src/js/jquery.steps.min.js',
        'static/src/js/website-tracknme.js',
        'static/src/js/website-choose-plan.js',
        'static/src/js/website-validate-card.js',
        'static/src/js/website-car-validate.js',
        'static/src/js/website-validate-password.js',
        'static/src/js/website_sale_payment.js',
           ],

    'css': ["static/src/css/jquery.steps.css",],

    'data': [
            'views/quick_sale_view.xml',
            'views/template_mail_view.xml',
            'views/schedule_action.xml',
            'views/register_vehicle_view.xml',
            'views/stock_production_lot_view.xml',
            'views/product_template_view.xml',
            'views/installation_schedule_view.xml',
            'views/ir_sequence_view.xml',
            'views/vehicle_category_view.xml',
            'views/vehicle_manufacturer_view.xml',
            'views/vehicle_model_view.xml',
            'views/vehicle_partner_view.xml',
            'views/vehicle_year_view.xml',
            'views/installation_type_view.xml',
            'views/res_partner_view.xml',
            'views/account_invoice_view.xml',
            'views/sale_view.xml',
            'views/data_site_view.xml',
            'views/website_plan.xml',
            'views/website_card_register.xml',
            'views/website_card_register_portal.xml',
            'views/website_scheduler.xml',
            'views/website_schedule_service_view.xml',
            'views/website_sale_menu.xml',
            'views/website_car_register.xml',
            'views/website_portal_invoice.xml',
            'views/website_terms.xml',
            'views/website_password.xml',
            'views/res_users_view.xml',
            'views/res_company_view.xml',
            'wizard/change_credit_card_wizard.xml',
            'views/mail_template_view.xml',
            'views/menu_view.xml',
            'views/website_payment_template.xml'
    ],

    'installable': True,
    'license': 'AGPL-3'
}
