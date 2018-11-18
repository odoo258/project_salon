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

from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    template_subscription_id = fields.Many2one('sale.subscription.template', string="Template Subscription")
    type_service = fields.Many2one('br_account.service.type', string=u"Tipo de Serviço")

    @api.onchange('type_service')
    def onchange_product_type_service(self):
        if self.type_service:
            return {'value':{'service_type_id':self.type_service.id}}
        return {'value':{}}