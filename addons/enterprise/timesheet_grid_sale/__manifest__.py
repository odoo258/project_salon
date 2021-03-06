# -*- coding: utf-8 -*-
{
    'name': "Sales Timesheet: Grid Support",

    'summary': "Configure timesheet invoicing",

    'description': """
        When invoicing timesheets, allows invoicing either all timesheets
        linked to an SO, or only the validated timesheets
    """,

    'category': 'Hidden',
    'version': '0.1',

    'depends': ['sale_timesheet', 'timesheet_grid'],
    'data': ['data.xml'],

    'auto_install': True,
}
