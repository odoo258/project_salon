# -*- encoding: utf-8 -*-
from odoo import api, fields, models, _

class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    nfe_access_key = fields.Char(u'NFE ACCESS KEY')
    supplier_invoice_number = fields.Char(u'Supplier Number')
    ind_final = fields.Char(u'Ind Final')
    ind_pres = fields.Char(u'Ind Pres')
    nfe_purpose = fields.Char(u'Nfe Purpose')
    date_in_out = fields.Datetime(u'Date out')
    date_hour_invoice = fields.Datetime(u'Date Hora Invoice')
    nfe_version = fields.Char(u'Version NFE')
    nat_op = fields.Char(u'Natureza da Operação')
