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

from odoo import fields, models

class BankFile(models.Model):
    _name = 'bank.file'
    _order = "date_time desc"

    file_type = fields.Selection([('remessa_cnab','Remessa CNAB'), ('remessa_pagfor','Remessa PagFor'), ('retorno_cnab','Retorno CNAB'), ('retorno_pagfor','Retorno PagFor'), ('extrato','Extrato')], 'File Type', required=True)
    bank_id = fields.Many2one('res.bank','Bank')
    filename = fields.Char('Filename', size=128, default='CNAB.txt')
    date_time = fields.Datetime('Date/Time')
    cnab_file = fields.Binary('CNAB File')