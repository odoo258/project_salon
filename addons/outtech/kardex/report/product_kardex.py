# -*- coding: utf-8 -*-

import re

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError
from odoo.osv import expression

import odoo.addons.decimal_precision as dp

class ProductPriceHistory(models.Model):
    _inherit = 'product.product'
    @api.multi
    def get_history_price(self, company_id, date=None):
        history = self.env['product.price.history'].search([
            ('company_id', '=', company_id),
            ('product_id', 'in', self.ids),
            ('datetime', '<=', date or fields.Datetime.now())], limit=1),

        if len(history) > 1:
            return history[-1].cost or 0.0
        else:
            return history[0].cost or 0.0