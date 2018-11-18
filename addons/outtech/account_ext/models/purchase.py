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
from odoo.addons import decimal_precision as dp

class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.depends('discount')
    def _compute_amount(self):
        prices = {}
        for line in self:
            if line.discount:
                prices[line.id] = line.price_unit
                # line.price_unit *= (1 - line.discount / 100.0)
        super(PurchaseOrderLine, self)._compute_amount()
        # restore prices
        for line in self:
            if line.discount:
                line.price_unit = prices[line.id]

    discount = fields.Float(string='Discount (%)', digits_compute=dp.get_precision('Discount'))
    price_total = fields.Monetary(compute='_compute_amount', string='Total', store=True)

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.depends('order_line.price_total')
    def _amount_all(self):
        super(PurchaseOrder, self)._amount_all()
        for order in self:
            discount_total = 0
            for l in order.order_line:
                total = l.product_qty * l.price_unit
                disc = total - (total * (1 - (l.discount or 0.0) / 100.0))
                discount_total += disc
            price_subtotal = sum(l.price_subtotal for l in order.order_line)
            price_total = sum(l.price_total for l in order.order_line)
            order.update({
                'amount_untaxed': price_subtotal,
                'amount_tax': price_total - price_subtotal,
                'amount_total': price_total,
                'total_tax': price_total - price_subtotal,
                'total_bruto': sum(l.valor_bruto for l in order.order_line),
                'total_desconto': discount_total,
            })

    total_bruto = fields.Float(string='Total Bruto ( = )', readonly=True, compute='_amount_all',
        digits=dp.get_precision('Account'), store=True)
    total_tax = fields.Float(string='Impostos ( + )', readonly=True, compute='_amount_all',
        digits=dp.get_precision('Account'), store=True)
    total_desconto = fields.Float(string='Desconto ( - )', store=True, digits=dp.get_precision('Account'),
        compute='_amount_all')
