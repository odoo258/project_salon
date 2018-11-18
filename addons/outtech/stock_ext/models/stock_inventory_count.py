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
from odoo.exceptions import UserError

class StockInventoryFirstCount(models.Model):
    _name = 'stock.inventory.first.count'

    product_id = fields.Many2one('product.product', string='Product')
    product_uom_id = fields.Many2one('product.uom', string='Unit of Measure')
    product_barcode = fields.Char(string='Barcode', size=15)
    stock_inventory_id = fields.Many2one('stock.inventory', string='Stock Inventory')
    quantity = fields.Float(string='Quantity')

    @api.onchange('product_barcode')
    def onchange_product_barcode(self):

        if self.product_barcode:

            src_product_product = self.env['product.product'].search([('barcode','=',self.product_barcode)])

            if len(src_product_product) == 1:

                self.product_id = src_product_product.id
                self.quantity = 1.00

        return False

    @api.onchange('product_id')
    def onchange_product_id(self):

        if self.product_id:

            self.product_uom_id = self.product_id.uom_id.id

        return False

class StockInventorySecondCount(models.Model):
    _name = 'stock.inventory.second.count'

    product_id = fields.Many2one('product.product', string='Product')
    product_uom_id = fields.Many2one('product.uom', string='Unit of Measure')
    product_barcode = fields.Char(string='Barcode')
    stock_inventory_id = fields.Many2one('stock.inventory', string='Stock Inventory')
    quantity = fields.Float(string='Quantity')

    @api.onchange('product_barcode')
    def onchange_product_barcode(self):

        if self.product_barcode:

            src_product_product = self.env['product.product'].search([('barcode', '=', self.product_barcode)])

            if len(src_product_product) == 1:
                self.product_id = src_product_product.id
                self.quantity = 1.00

        return False

    @api.onchange('product_id')
    def onchange_product_id(self):

        if self.product_id:
            self.product_uom_id = self.product_id.uom_id.id

        return False

class StockInventoryThirdCount(models.Model):
    _name = 'stock.inventory.third.count'

    product_id = fields.Many2one('product.product', string='Product')
    product_uom_id = fields.Many2one('product.uom', string='Unit of Measure')
    product_barcode = fields.Char(string='Barcode')
    stock_inventory_id = fields.Many2one('stock.inventory', string='Stock Inventory')
    quantity = fields.Float(string='Quantity')

    @api.onchange('product_barcode')
    def onchange_product_barcode(self):

        if self.product_barcode:

            src_product_product = self.env['product.product'].search([('barcode', '=', self.product_barcode)])

            if len(src_product_product) == 1:
                self.product_id = src_product_product.id
                self.quantity = 1.00

        return False

    @api.onchange('product_id')
    def onchange_product_id(self):

        if self.product_id:
            self.product_uom_id = self.product_id.uom_id.id

        return False


class StockInventoryLine(models.Model):
    _inherit = 'stock.inventory.line'

    qty_first_count = fields.Float('First Count Quantity', digits=dp.get_precision('Product Unit of Measure'), default=0)
    qty_second_count = fields.Float('Second Count Quantity', digits=dp.get_precision('Product Unit of Measure'), default=0)
    qty_third_count = fields.Float('Third Count Quantity', digits=dp.get_precision('Product Unit of Measure'), default=0)
    reconciled = fields.Boolean('Reconciled', default=False)

class StockInventory(models.Model):
    _inherit = "stock.inventory"

    first_count_ids = fields.One2many('stock.inventory.first.count', 'stock_inventory_id', string='First Counts')
    second_count_ids = fields.One2many('stock.inventory.second.count', 'stock_inventory_id', string='Second Counts')
    third_count_ids = fields.One2many('stock.inventory.third.count', 'stock_inventory_id', string='Third Counts')
    state = fields.Selection(string='Status', selection=[
        ('draft', 'Draft'),
        ('cancel', 'Cancelled'),
        ('confirm', 'In Progress'),
        ('first_count','1st Count'),
        ('second_count','2nd Count'),
        ('third_count','3rd Count'),
        ('done', 'Validated')],
                             copy=False, index=True, readonly=True,
                             default='draft')
    responsible_first_count = fields.Many2one('res.users', string='Responsible for the 1st Count')
    responsible_second_count = fields.Many2one('res.users', string='Responsible for the 2nd Count')
    responsible_third_count = fields.Many2one('res.users', string='Responsible for the 3rd Count')
    inventory_adjustments_verification = fields.Boolean('Inventory Adjustments with Verification')

    @api.multi
    def action_start_verification(self):
        for inventory in self:
            vals = {'state_verification': 'first_count', 'date': fields.Datetime.now()}
            if (inventory.filter != 'partial') and not inventory.line_ids:
                vals.update(
                    {'line_ids': [(0, 0, line_values) for line_values in inventory._get_inventory_lines_values()]})
            inventory.write(vals)
        return True

    prepare_inventory_verification = action_start_verification

    @api.multi
    def validation_lines_stock(self, line_ids):

        products = []

        for line in line_ids:

            if not line.product_id.id in products:

                products.append(line.product_id.id)

            else:
                return False

        return True



    @api.multi
    def action_validate_first_count(self):

        first_count_products = {}
        products_list = []
        necessary_second_count = False

        for inventory in self:

            # Validation for no repeat products in verification

            if not self.validation_lines_stock(inventory.line_ids):
                raise UserError(_('There is more than one product on the checklist, check again and choose only once each product!'))

            if not inventory.responsible_first_count:
                raise UserError(_('No responsible for validate first count, please include a responsible!'))

            if not inventory.first_count_ids:
                raise UserError(_('No products for validate first count, please include at least one product!'))

            for item_first_count in inventory.first_count_ids:

                if not item_first_count.product_id:
                    continue

                if item_first_count.quantity < 0.00:
                    raise UserError(_('Exist product(s) with quantity less than 0.00, please check first count products!'))

                product_id = item_first_count.product_id.id

                if product_id in products_list:

                    first_count_products.update({product_id: item_first_count.quantity + first_count_products[product_id]})

                else:
                    first_count_products.update({product_id: item_first_count.quantity})
                    products_list.append(product_id)

            for line_inventory in inventory.line_ids:

                if line_inventory.reconciled:
                    continue

                if line_inventory.product_id.id in products_list:
                    line_inventory.qty_first_count = first_count_products[line_inventory.product_id.id]
                else:
                    raise UserError(_('At the first count there are not all products that should be accounted! Add the products, even if the quantity 0.00.'))

                if line_inventory.qty_first_count == line_inventory.theoretical_qty:

                    line_inventory.product_qty = line_inventory.qty_first_count
                    line_inventory.reconciled = True

                else:
                    necessary_second_count = True

            if necessary_second_count:

                inventory.state = 'second_count'

            else:

                inventory.action_check()
                inventory.write({'state': 'done'})
                inventory.post_inventory()

        return True

    @api.multi
    def action_validate_second_count(self):

        second_count_products = {}
        products_list = []
        necessary_third_count = False

        for inventory in self:

            if not inventory.responsible_second_count:
                raise UserError(_('No responsible for validate second count, please include a responsible!'))

            if not inventory.second_count_ids:
                raise UserError(_('No products for validate second count, please include at least one product!'))

            for item_second_count in inventory.second_count_ids:

                if not item_second_count.product_id:
                    continue

                if item_second_count.quantity < 0.00:
                    raise UserError( _('Exist product(s) with quantity less than 0.00, please check second count products!'))

                product_id = item_second_count.product_id.id

                if product_id in products_list:

                    second_count_products.update(
                        {product_id: item_second_count.quantity + second_count_products[product_id]})

                else:
                    second_count_products.update({product_id: item_second_count.quantity})
                    products_list.append(product_id)

            for line_inventory in inventory.line_ids:

                if line_inventory.reconciled:
                    continue

                if line_inventory.product_id.id in products_list:
                    line_inventory.qty_second_count = second_count_products[line_inventory.product_id.id]
                else:
                    raise UserError(_('At the second count there are not all products that should be accounted! Add the products, even if the quantity 0.00.'))

                if line_inventory.qty_second_count == line_inventory.theoretical_qty or line_inventory.qty_second_count == line_inventory.qty_first_count:

                    line_inventory.product_qty = line_inventory.qty_second_count
                    line_inventory.reconciled = True

                else:
                    necessary_third_count = True

            if necessary_third_count:

                inventory.state = 'third_count'

            else:

                inventory.action_check()
                inventory.write({'state': 'done'})
                inventory.post_inventory()

        return True

    @api.multi
    def action_validate_third_count(self):

        third_count_products = {}
        products_list = []

        for inventory in self:

            if not inventory.responsible_third_count:
                raise UserError(_('No responsible for validate third count, please include a responsible!'))

            if not inventory.third_count_ids:
                raise UserError(_('No products for validate third count, please include at least one product!'))

            for item_third_count in inventory.third_count_ids:

                if not item_third_count.product_id:
                    continue

                if item_third_count.quantity < 0.00:
                    raise UserError( _('Exist product(s) with quantity less than 0.00, please check third count products!'))

                product_id = item_third_count.product_id.id

                if product_id in products_list:

                    third_count_products.update(
                        {product_id: item_third_count.quantity + third_count_products[product_id]})

                else:
                    third_count_products.update({product_id: item_third_count.quantity})
                    products_list.append(product_id)

            for line_inventory in inventory.line_ids:

                if line_inventory.reconciled:
                    continue

                if line_inventory.product_id.id in products_list:
                    line_inventory.qty_third_count = third_count_products[line_inventory.product_id.id]
                    line_inventory.product_qty = line_inventory.qty_third_count
                    line_inventory.reconciled = True
                else:
                    raise UserError(_('At the third count there are not all products that should be accounted! Add the products, even if the quantity 0.00.'))

            inventory.action_check()
            inventory.write({'state': 'done'})
            inventory.post_inventory()

        return True

    @api.multi
    def action_cancel_inventory_verification(self):

        for inventory in self:
            inventory.write({'state': 'cancel'})

    @api.multi
    def action_start(self):
        for inventory in self:
            vals = {'state': 'first_count', 'date': fields.Datetime.now()}
            if (inventory.filter != 'partial') and not inventory.line_ids:
                vals.update(
                    {'line_ids': [(0, 0, line_values) for line_values in inventory._get_inventory_lines_values()]})
            inventory.write(vals)
        return True

    prepare_inventory_verification = action_start

    @api.multi
    def action_done_second(self):
        # for inventory in self:
        #     vals = {'state': 'first_count', 'date': fields.Datetime.now()}
        #     if (inventory.filter != 'partial') and not inventory.line_ids:
        #         vals.update(
        #             {'line_ids': [(0, 0, line_values) for line_values in inventory._get_inventory_lines_values()]})
        #     inventory.write(vals)
        return True

    action_done_second = action_done_second

    @api.multi
    def action_done_third(self):
        # for inventory in self:
        #     vals = {'state': 'first_count', 'date': fields.Datetime.now()}
        #     if (inventory.filter != 'partial') and not inventory.line_ids:
        #         vals.update(
        #             {'line_ids': [(0, 0, line_values) for line_values in inventory._get_inventory_lines_values()]})
        #     inventory.write(vals)
        return True

    action_done_third = action_done_third

    @api.multi
    def action_cancel_verification(self):
        self.mapped('move_ids').action_cancel()
        self.write({
            'line_ids': [(5,)],
            'state_verification': 'draft'
        })