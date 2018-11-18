# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from dhl_request import DHLProvider

from odoo import models, fields, _


class Providerdhl(models.Model):
    _inherit = 'delivery.carrier'

    delivery_type = fields.Selection(selection_add=[('dhl', "DHL")])

    dhl_SiteID = fields.Char(string="DHL SiteID", groups="base.group_system")
    dhl_password = fields.Char(string="DHL Password", groups="base.group_system")
    dhl_account_number = fields.Char(string="DHL Account Number", groups="base.group_system")
    dhl_package_dimension_unit = fields.Selection([('IN', 'Inches'),
                                                   ('CM', 'Centimeters')],
                                                  default='CM',
                                                  string='Package Dimension Unit')
    dhl_package_weight_unit = fields.Selection([('LB', 'Pounds'),
                                                ('KG', 'Kilograms')],
                                               default='KG',
                                               string="Package Weight Unit")
    dhl_default_packaging_id = fields.Many2one('product.packaging', string='DHL Default Packaging Type')
    dhl_region_code = fields.Selection([('AP', 'Asia Pacific'),
                                        ('AM', 'America'),
                                        ('EU', 'Europe')],
                                       default='AM',
                                       string='Region')
    # Nowadays hidden, by default it's the D, couldn't find any documentation on other services
    dhl_product_code = fields.Selection([('D', 'D - Express Worldwide'),
                                         ('T', 'T - Express 12:00'),
                                         ('K', 'K - Express 9:00'),
                                         ('N', 'N - Domestic Express'),
                                         ],
                                        default='D',
                                        string='Product')
    dhl_dutiable = fields.Boolean(string="Dutiable Material", help="Check this if your package is dutiable.")
    dhl_label_image_format = fields.Selection([
        ('EPL2', 'EPL2'),
        ('PDF', 'PDF'),
        ('ZPL2', 'ZPL2'),
    ], string="Label Image Format", default='PDF')
    dhl_label_template = fields.Selection([
        ('8X4_A4_PDF', '8X4_A4_PDF'),
        ('8X4_thermal', '8X4_thermal'),
        ('8X4_A4_TC_PDF', '8X4_A4_TC_PDF'),
        ('6X4_thermal', '6X4_thermal'),
        ('6X4_A4_PDF', '6X4_A4_PDF'),
        ('8X4_CI_PDF', '8X4_CI_PDF'),
        ('8X4_CI_thermal', '8X4_CI_thermal'),
        ('8X4_RU_A4_PDF', '8X4_RU_A4_PDF'),
        ('6X4_PDF', '6X4_PDF'),
        ('8X4_PDF', '8X4_PDF')
    ], string="Label Template", default='8X4_A4_PDF')

    def dhl_get_shipping_price_from_so(self, orders):
        res = []
        srm = DHLProvider(self.prod_environment)
        for order in orders:
            srm.check_required_value(self, order.partner_shipping_id, order.warehouse_id.partner_id, order=order)
            result = srm.rate_request(order, self)
            if order.currency_id.name == result['currency']:
                price = float(result['price'])
            else:
                quote_currency = self.env['res.currency'].search([('name', '=', result['currency'])], limit=1)
                price = quote_currency.compute(float(result['price']), order.currency_id)
            res = res + [price]
        return res

    def dhl_send_shipping(self, pickings):
        res = []

        srm = DHLProvider(self.prod_environment)
        for picking in pickings:
            shipping = srm.send_shipping(picking, self)
            order_currency = picking.sale_id.currency_id or picking.company_id.currency_id
            if order_currency.name == shipping['currency']:
                carrier_price = float(shipping['price'])
            else:
                quote_currency = self.env['res.currency'].search([('name', '=', shipping['currency'])], limit=1)
                carrier_price = quote_currency.compute(float(shipping['price']), order_currency)
            carrier_tracking_ref = shipping['tracking_number']
            logmessage = (_("Shipment created into DHL <br/> <b>Tracking Number : </b>%s") % (carrier_tracking_ref))
            picking.message_post(body=logmessage, attachments=[('LabelDHL-%s.%s' % (carrier_tracking_ref, self.dhl_label_image_format), srm.save_label())])
            shipping_data = {
                'exact_price': carrier_price,
                'tracking_number': carrier_tracking_ref
            }
            res = res + [shipping_data]

        return res

    def dhl_get_tracking_link(self, pickings):
        res = []
        for picking in pickings:
            res = res + ['http://www.dhl.com/en/express/tracking.html?AWB=%s' % picking.carrier_tracking_ref]
        return res

    def dhl_cancel_shipment(self, picking):
        # Obviously you need a pick up date to delete SHIPMENT by DHL. So you can't do it if you didn't schedule a pick-up.
        picking.message_post(body=_(u"You can't cancel DHL shipping without pickup date."))
        picking.write({'carrier_tracking_ref': '',
                       'carrier_price': 0.0})
