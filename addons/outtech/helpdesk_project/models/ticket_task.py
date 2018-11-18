# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class task(models.Model):
    _inherit = 'project.task'

    ticket_id = fields.Many2one('helpdesk.ticket', 'Ticket')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
