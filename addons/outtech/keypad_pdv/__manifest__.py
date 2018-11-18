# -*- encoding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (c) 2010-2012 Elico Corp. All Rights Reserved.
#    Author: Rafael Lima <rafaelslima.py@gmail.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################



{
    'name': "Keypad PDV",
    'version': '10.0.1',
    'summary': 'Teclado numérico aos Popups do PDV',
    'category': 'Tools',
    'description': """Este módulo adiciona ao PDV a opção de entrada de dados via teclado numérico nas janelas de Popups""",
    'author': 'Rafael Lima @ Outtech',
    'license': 'AGPL-3',
    'website': "www.outtech.com.br",
    "depends" : ['web', 'point_of_sale'],
    'data': [
        'keypad_pdv.xml'
    ],
    "installable": True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: