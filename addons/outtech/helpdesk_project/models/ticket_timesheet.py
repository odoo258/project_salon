# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class account_analytic_line(models.Model):
    _inherit = 'account.analytic.line'

    ticket_id = fields.Many2one('helpdesk.ticket', 'Helpdesk Ticket')
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
