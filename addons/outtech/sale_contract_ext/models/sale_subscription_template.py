# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.addons.br_account.models.cst import CST_ICMS
from odoo.addons.br_account.models.cst import CSOSN_SIMPLES
from odoo.addons.br_account.models.cst import CST_IPI
from odoo.addons.br_account.models.cst import CST_PIS_COFINS

class SaleSubscriptionTemplate(models.Model):
    _inherit = "sale.subscription.template"

    cst_icms = fields.Selection(CST_ICMS, string="CST ICMS")
    csosn_icms = fields.Selection(CSOSN_SIMPLES, string="CSOSN ICMS")
    cst_pis = fields.Selection(CST_PIS_COFINS, string="CST PIS")
    cst_cofins = fields.Selection(CST_PIS_COFINS, string="CST COFINS")
    cst_ipi = fields.Selection(CST_IPI, string="CST IPI")