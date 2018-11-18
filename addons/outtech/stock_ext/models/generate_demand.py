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
from lxml import etree
from datetime import datetime
from datetime import date
from odoo.addons import decimal_precision as dp
from dateutil.relativedelta import relativedelta


class GenerateDemand(models.Model):
    _name = "generate.demand"

    def _default_picking_type(self):
        company_id = self.env.user.company_id
        if company_id:
            picking_type = company_id.default_picking_type.id
        else:
            picking_type = False
        # picking_types = self.env['stock.picking.type'].search([('company_id','=',company_id)])
        return picking_type

    def _get_warehouse(self):
        warehouse_ids = self.env['stock.warehouse'].search([('company_id','=',self.env.user.company_id.id)])
        if warehouse_ids:
            domain = "[('warehouse_id','in',%s)]" % warehouse_ids.ids
            return domain
        else:
            domain = ""
            return domain

    stock_location_id = fields.Many2one('stock.location', string=_('Location'))
    picking_type_select = fields.Many2one('stock.picking.type', string=_('Picking Type'), domain=_get_warehouse)
    warehouse_id = fields.Many2one('res.company','Company')
    location_ids = fields.Many2many('stock.location', string=_('Locations'))

    def run_stock_calculation(self):
        product_obj = self.env["product.template"]
        location_ids = self.env['stock.location'].browse(self.location_ids.ids)

        product_ids = product_obj.search([('purchase_ok','=',True),('sale_ok','=',True),('type','=','product')])
        for line in product_ids:
            product_src = self.env['product.product'].search([('product_tmpl_id','=',line.id)])
            if not product_src:
                continue

            for product_id in product_src:
                value = 0
                date_today = date.today()

                first_move_date = datetime.today()
                location_dest = self.env["stock.location"].search([('usage','=','customer')]).id
                begin_date = str(datetime.today() - relativedelta(days=365))
                query = "select id from stock_pack_operation where location_dest_id in (%s) and qty_done > 0 and product_id = %s and picking_id in (select id from stock_picking where min_date >= '%s')" \
                        % (str(location_dest).replace('[','(').replace(']',')'), product_id.id, str(begin_date))
                self._cr.execute(query)
                stock_pack_ids = set(row[0] for row in self._cr.fetchall())
                for stock_picking_id in self.env["stock.pack.operation"].browse(stock_pack_ids):
                    if stock_picking_id.picking_id.min_date:
                        date_move = datetime.strptime(stock_picking_id.picking_id.min_date, "%Y-%m-%d %H:%M:%S")
                        value += stock_picking_id.qty_done
                        if date_move <= first_move_date:
                            first_move_date = date_move
                if value < 0:
                    value = 0

                date_calc = first_move_date.date()

                date_range = (date_today - date_calc).days
                for location_id in location_ids:
                    reorder_rule_id = self.env["stock.warehouse.orderpoint"].search([('product_id', '=', product_id.id), ('location_id', '=', location_id.id)])
                    days_of_coverage = 0
                    if location_id.is_store:
                        days = 26
                    else:
                        days = 30

                    if line.seller_ids and location_id.is_store == False:
                        seller_delay = product_id.seller_ids[0].delay
                    else:
                        seller_delay = 0

                    if location_id.is_store == False:
                        days_of_coverage += float(seller_delay)

                    if product_id.days_of_coverage > 0:
                        days_of_coverage += (float(product_id.days_of_coverage))
                    else:
                        days_of_coverage += 1

                    if (date_range > 360):
                        date_range = 12
                    elif (date_range < 31):
                        date_range = 1
                    else:
                        date_range = date_range / 30
                        date_range = int(date_range)

                    days_average = value / float(date_range)
                    average = days_average / days

                    minimum_stock = average * days_of_coverage

                    if reorder_rule_id:
                        for reorder in reorder_rule_id:
                            vals = {
                                'product_max_qty': minimum_stock,
                                'product_min_qty': minimum_stock,
                                'qty_multiple': reorder.qty_multiple,
                                'product_uom': reorder.product_uom,
                                'lead_days': reorder.lead_days,
                                'months_divided': date_range,
                            }
                            reorder.write(vals)
                    else:
                         vals_create = {
                             'product_id': product_id.id,
                             'product_uom': product_id.uom_id.id,
                             'product_min_qty': minimum_stock,
                             'product_max_qty': minimum_stock,
                             'location_id': location_id.id,
                             'months_divided': date_range,
                         }
                         self.env["stock.warehouse.orderpoint"].create(vals_create)

        print("Sucesso")

class ResCompany(models.Model):
    _inherit = 'res.company'

    default_picking_type = fields.Many2one('stock.picking.type', string="Default Picking Type", default=False)
    generate_demand_date = fields.Date('Generate Demand Date')

class StockWarehouseOrderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    product_min_qty = fields.Float(
        'Minimum Quantity', digits=dp.get_precision('Minimum Stock Precision'), required=True,
        help="When the virtual stock goes below the Min Quantity specified for this field, Odoo generates "
             "a procurement to bring the forecasted quantity to the Max Quantity.")
    product_max_qty = fields.Float(
        'Maximum Quantity', digits=dp.get_precision('Minimum Stock Precision'), required=True,
        help="When the virtual stock goes below the Min Quantity, Odoo generates "
             "a procurement to bring the forecasted quantity to the Quantity specified as Max Quantity.")
    months_divided = fields.Char("Meses Divididos")