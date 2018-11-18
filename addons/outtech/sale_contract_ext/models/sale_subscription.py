# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError

import odoo.addons.decimal_precision as dp

_logger = logging.getLogger(__name__)


class SaleSubscription(models.Model):
    _inherit = "sale.subscription"



    @api.multi
    def _prepare_invoice_line(self, line, fiscal_position):
        if 'force_company' in self.env.context:
            company = self.env['res.company'].browse(self.env.context['force_company'])
        else:
            company = line.analytic_account_id.company_id
            line = line.with_context(force_company=company.id, company_id=company.id)

        account = line.product_id.property_account_income_id
        if not account:
            account = line.product_id.categ_id.property_account_income_categ_id
        account_id = fiscal_position.map_account(account).id
        tax = line.product_id.taxes_id.filtered(lambda r: r.company_id == company)
        tax = fiscal_position.map_tax(tax)
        res = {
            'name': line.name,
            'account_id': account_id,
            'account_analytic_id': line.analytic_account_id.analytic_account_id.id,
            'price_unit': line.price_unit or 0.0,
            'discount': line.discount,
            'quantity': line.quantity,
            'uom_id': line.uom_id.id,
            'product_id': line.product_id.id,
            'product_type': line.product_id.fiscal_type,
            'invoice_line_tax_ids': [(6, 0, tax.ids)],
        }
        # Incluindo Impostos de Serviço em faturas
        # Improve this one later
        icms = tax.filtered(lambda x: x.domain == 'icms')
        icmsst = tax.filtered(lambda x: x.domain == 'icmsst')
        icms_inter = tax.filtered(lambda x: x.domain == 'icms_inter')
        icms_intra = tax.filtered(lambda x: x.domain == 'icms_intra')
        icms_fcp = tax.filtered(lambda x: x.domain == 'icms_fcp')
        simples = tax.filtered(lambda x: x.domain == 'simples')
        ipi = tax.filtered(lambda x: x.domain == 'ipi')
        pis = tax.filtered(lambda x: x.domain == 'pis')
        cofins = tax.filtered(lambda x: x.domain == 'cofins')
        ii = tax.filtered(lambda x: x.domain == 'ii')
        issqn = tax.filtered(lambda x: x.domain == 'issqn')

        res['tax_icms_id'] = icms and icms.id or False
        res['tax_icms_st_id'] = icmsst and icmsst.id or False
        res['tax_icms_inter_id'] = icms_inter and icms_inter.id or False
        res['tax_icms_intra_id'] = icms_intra and icms_intra.id or False
        res['tax_icms_fcp_id'] = icms_fcp and icms_fcp.id or False
        res['tax_simples_id'] = simples and simples.id or False
        res['tax_ipi_id'] = ipi and ipi.id or False
        res['tax_pis_id'] = pis and pis.id or False
        res['tax_cofins_id'] = cofins and cofins.id or False
        res['tax_ii_id'] = ii and ii.id or False
        res['tax_issqn_id'] = issqn and issqn.id or False

        service = line.product_id.service_type_id

        valor = 0
        if line.product_id.fiscal_type == 'service':
            valor = line.product_id.lst_price * (
                service.federal_nacional + service.estadual_imposto +
                service.municipal_imposto) / 100

        res['tributos_estimados'] = valor

        res['pis_cst'] = self.template_id.cst_pis
        res['pis_aliquota'] = pis.amount or 0.0

        res['cofins_cst'] = self.template_id.cst_cofins
        res['cofins_aliquota'] = cofins.amount or 0.0

        res['issqn_aliquota'] = issqn.amount or 0.0

        res['ii_aliquota'] = ii.amount or 0.0
        return res
