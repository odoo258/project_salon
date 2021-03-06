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

from odoo import models, fields

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    automatic_process = fields.Boolean(string='Process Automatic')
    log_ids = fields.One2many('account.invoice.log', 'invoice_id', 'Logs')
    sale_id =  fields.Many2one('sale.order','Sale Order')

class AccountInvoiceLog(models.Model):
    _name = 'account.invoice.log'

    invoice_id = fields.Many2one('account.invoice', 'Logs')
    quick_sale_id = fields.Many2one('quick.sale', 'Logs')
    log = fields.Char('Logs')
