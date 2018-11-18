# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 KMEE (http://www.kmee.com.br)
#    @author Luis Felipe Miléo <mileo@kmee.com.br>
#             Danimar Ribeiro <danimaribeiro@gmail.com>
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
    'name': 'Importação de Documento Fiscal Eletronico de Compra',
    'version': '10.0.1.0.0',
    'category': 'Account',
    'license': 'AGPL-3',
    'author': 'Outtech',
    'website': 'http://www.outtech.com.br',
    'external_dependencies': {
        'python': ['pysped'],
    },
    'depends': [
        'account'
    ],
    'data': [
        'wizard/account_invoice_import.xml',
        # 'views/account_fiscal_position_view.xml',
        # 'views/account_invoice_view.xml',
        'views/nfe_import_view.xml',
    ],
    'css': ['static/src/css/nfe_import.css'],
    'active': False,
    "installable": True,
    "auto_install": False,
}
