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

from odoo import api, fields, models, _
import logging
import re

class Partner(models.Model):
    """ Every change made on any res_partner field will be shown on the message log """

    _name = "res.partner"
    _inherit = ['res.partner']

    @api.multi
    def write(self, vals):
        res = super(Partner, self).write(vals)

        body = _('Updated fields: <ul>')
        for key, val in vals.items():
            field_label = self._fields[key].string
            field_translation = self.env['ir.translation'].search([('src', '=', field_label),('lang','=',self.env.user.lang)])
            if field_translation:
                body += '<li><b>%s</b>: %s</li>' % (field_translation[0].value, val)
            else:
                body += '<li><b>%s</b>: %s</li>' % (field_label, val)

        body += '</ul>'
        self.message_post(body=body, subject=_("Records Updated"))
        return res
