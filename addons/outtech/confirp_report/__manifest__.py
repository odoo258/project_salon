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
    'name': 'Confirp Report',
    'version': '001.01',
    'author': 'Outtech',
    'maintainer': 'Outtech',
    'website': 'http://www.outtech.com.br/',
    'category': 'account',
    'sequence': 20,
    'summary': 'Confirp Report',
    'description': """
    This modules prints a accounting report for the Confirp.
    """,
    'depends': ['account'],
    'data': ['views/account_view.xml',
             'views/confirp_report_download.xml'],
    'installable': True,
}
