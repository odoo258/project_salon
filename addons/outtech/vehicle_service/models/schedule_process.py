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

from odoo import api, models, fields
import requests as req
from datetime import date

class ScheduleProcess(models.Model):
    _name = 'schedule.process'

    def accounting_process(self):
        invoices = self.env['account.invoice'].search([('automatic_process','=',True),('state','in',['draft','open'])])
        for inv in invoices:
            if inv.invoice_line_ids:
                self.env['request.php'].recurrency_payment(inv)
        return True


