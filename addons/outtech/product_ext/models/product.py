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
import odoo.addons.decimal_precision as dp
from functools import reduce
from odoo.exceptions import ValidationError
from odoo.addons.br_account.models.cst import CST_ICMS
from odoo.addons.br_account.models.cst import CSOSN_SIMPLES
from odoo.addons.br_account.models.cst import CST_IPI
from odoo.addons.br_account.models.cst import CST_PIS_COFINS

class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.one
    @api.constrains('default_code')
    def _check_unicity_name(self):
        if self.default_code:
            domain = [('default_code', '=', self.default_code)]

            if len(self.search(domain)) > 1:
                raise ValidationError(_('"Default Code" Should be unique'))

    percent_sale_value = fields.Float(string='Percent for value calculation for sale(%)')
    cost_value = fields.Float(string='Cost for value calculation for sale(%)')
    suggested_sale_value = fields.Float(string='Suggested for Sale', readonly=True)
    suggested_sale_value_invible = fields.Float(string='Suggested for Sale')
    promotional_price = fields.Float(string='Promotional Price', digits=dp.get_precision('Product Price'))
    manufacturer_id = fields.Many2one('res.partner', string='Manufacturer', domain=[('manufacturer','=',True)])
    days_of_coverage = fields.Integer("Days of Coverage")
    barcode = fields.Char('Barcode', oldname='ean13', related='product_variant_ids.barcode')
    default_code = fields.Char('Internal Reference', compute='_compute_default_code', inverse='_set_default_code', store=True)

    #Sat Emissão de cupons configuração
    cfop_sat_id = fields.Many2one('br_account.cfop', string=u"CFOP Cupom Fiscal")
    icms_sat_csosn = fields.Selection(CSOSN_SIMPLES, string=u'CSOSN ICMS')
    icms_sat_cst = fields.Selection(CST_ICMS, string=u'CST ICMS')
    ipi_sat_cst = fields.Selection(CST_IPI, string=u'CST IPI')
    pis_sat_cst = fields.Selection(CST_PIS_COFINS, string=u'CST PIS')
    cofins_sat_cst = fields.Selection(CST_PIS_COFINS, string=u'CST COFINS')

    # @api.onchange('barcode')
    # def calculate_checksum(self):
    #     #self.env.user.company_id.currency_id.compute(self.company_id.po_double_validation_amount, self.currency_id):
    #     #if self.env.user.company_id.product_ids.compute(self.company_id.check_barcode, self.product_ids):
    #     #if self.env['res.config.settings'].check_barcode: #.company_id.product_ids.compute(self.company_id.check_barcode, self.product_ids):
    #     if self.check_barcode_invisible == 'True':
    #         if self.barcode:
    #             barcode = self.barcode[:12]
    #             if len(barcode) < 12:
    #                 barcode = barcode.ljust(12, '0')
    #
    #
    #             sum_ = lambda x, y: int(x) + int(y)
    #             evensum = reduce(sum_, barcode[::2])
    #             oddsum = reduce(sum_, barcode[1::2])
    #             digit = (10 - ((evensum + oddsum * 3) % 10)) % 10
    #             self.write(
    #                 {
    #                     'barcode': barcode + str(digit)
    #                 }
    #         )
    #         else:
    #             return False


    @api.onchange('percent_sale_value', 'cost_value')
    def calc_suggested_value_sale(self):
        res = {'value':{}}
        if self.percent_sale_value > 0:
            val = self.cost_value * (1 + self.percent_sale_value/100)
            res['value']['suggested_sale_value'] = val
            res['value']['suggested_sale_value_invible'] = val
        else:
            val = 0
            res['value']['suggested_sale_value'] = val
            res['value']['suggested_sale_value_invible'] = val
        return res

    @api.multi
    def write(self, vals):
        if 'suggested_sale_value_invible' in vals:
            vals['suggested_sale_value'] = vals['suggested_sale_value_invible']
        return super(ProductTemplate, self).write(vals)

    @api.model
    def create(self, vals):
        if 'suggested_sale_value_invible' in vals:
            vals['suggested_sale_value'] = vals['suggested_sale_value_invible']
        return super(ProductTemplate, self).create(vals)

class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        # procutds_qtd = len(self.env['product.product'].search([('purchase_ok','=',True)]))
        # if limit > 8:
        #     limit = procutds_qtd
        return super(ProductProduct, self).name_search(name, args, operator=operator, limit=limit)