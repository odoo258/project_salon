# -*- coding: utf-8 -*-
# © 2016 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp
from odoo.tools.float_utils import float_is_zero, float_compare
from odoo.exceptions import ValidationError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'


    @api.multi
    def button_confirm(self):
        #result = super(PurchaseOrder, self).button_confirm()
        for order in self:
            if order.state not in ['draft', 'sent']:
                continue
            order._add_supplier_to_product()
            # Deal with double validation process
            if order.company_id.po_double_validation == 'one_step':
                order.button_approve(force=True)
            elif self.company_id.po_double_validation == 'two_step' \
                    and self.amount_total <= self.env.user.company_id.currency_id.compute(self.company_id.po_double_validation_amount, self.currency_id):
                        order.write({'state': 'purchase'})
            elif self.company_id.po_double_validation == 'two_step' \
                    and self.amount_total > self.env.user.company_id.currency_id.compute(self.company_id.po_double_validation_amount, self.currency_id):
                        order.write({'state': 'to approve'})
        return True

        for line in self.order_line:
            if line.price_total <= 0:
                raise ValidationError(_('You cannot confirm a quotation with total price equal or lower than 0.'))
        return result

    @api.depends('picking_ids')
    def _compute_picking_status(self):
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        for order in self:
            if self.env.user.company_id.id == order.sudo().company_id.id and order.sudo().state not in ['done','purchase'] :
                if all(float_compare(line.sudo().qty_received, line.sudo().product_qty, precision_digits=precision) >= 0 for line in order.sudo().order_line):
                    order.sudo().picking_status = 'ok'
                else:
                    if any(line.sudo().qty_received > 1 for line in order.sudo().order_line):
                        order.sudo().picking_status = 'partial'
                    else:
                        order.sudo().picking_status = 'not_picking'

    picking_status =  fields.Selection([('not_picking','Not Picking'),('partial','Parcial Picking'),('ok','Picking')],\
                                       'Picking Status', compute='_compute_picking_status',store=True, readonly=True, copy=False, default='not_picking')

    @api.multi
    def write(self, vals):
        res = super(PurchaseOrder, self).write(vals)
        return res