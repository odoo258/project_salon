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
from odoo.exceptions import UserError, RedirectWarning
from odoo.addons import decimal_precision as dp

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def _compute_amount(self):
        super(AccountInvoice, self)._compute_amount()
        lines = self.invoice_line_ids

        self.total_seguro = sum(l.valor_seguro for l in lines)
        self.total_frete = sum(l.valor_frete for l in lines)
        self.total_despesas = sum(l.outras_despesas for l in lines)
        if self.purchase_origin_id:
            if self.total_seguro !=  self.purchase_origin_id.total_seguro:
                seguro = self.purchase_origin_id.total_seguro - self.total_seguro
                lines[0].valor_seguro = lines[0].valor_seguro + seguro
            if self.total_frete !=  self.purchase_origin_id.total_frete:
                frete = self.purchase_origin_id.total_frete - self.total_frete
                lines[0].valor_frete = lines[0].valor_frete + frete
            if self.total_despesas !=  self.purchase_origin_id.total_despesas:
                despesas = self.purchase_origin_id.total_despesas - self.total_despesas
                lines[0].outras_despesas = lines[0].outras_despesas + despesas
        self.amount_total = self.total_bruto - self.total_desconto + \
            self.total_tax + self.total_frete + self.total_seguro + \
            self.total_despesas
        sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
        self.amount_total_company_signed = self.amount_total * sign
        self.amount_total_signed = self.amount_total * sign

    total_seguro = fields.Float(
        string='Seguro ( + )', digits=dp.get_precision('Account'),
        compute="_compute_amount")
    total_despesas = fields.Float(
        string='Despesas ( + )', digits=dp.get_precision('Account'),
        compute="_compute_amount")
    total_frete = fields.Float(
        string='Frete ( + )', digits=dp.get_precision('Account'),
        compute="_compute_amount")


    @api.onchange('partner_id', 'company_id')
    def _onchange_partner_id(self):
        account_id = False
        term_id = self.payment_term_id
        payment_term_id = False
        position_id = self.fiscal_position_id
        fiscal_position = False
        bank_id = False
        company_id = self.company_id.id
        p = self.partner_id if not company_id else self.partner_id.with_context(force_company=company_id)
        type = self.type
        if p:
            rec_account = p.property_account_receivable_id
            pay_account = p.property_account_payable_id
            if not rec_account and not pay_account:
                action = self.env.ref('account. action_account_config')
                msg = _('Cannot find a chart of accounts for this company, You should configure it. \nPlease go to Account Configuration.')
                raise RedirectWarning(msg, action.id, _('Go to the configuration panel'))

            if type in ('out_invoice', 'out_refund'):
                if not self.fiscal_position_id.account_id.id:
                    account_id = rec_account.id
                else:
                    account_id = self.fiscal_position_id.account_id.id
                payment_term_id = p.property_payment_term_id.id
            else:
                if not self.fiscal_position_id.account_id.id:
                    account_id = pay_account.id
                else:
                    account_id = self.fiscal_position_id.account_id.id
                payment_term_id = p.property_supplier_payment_term_id.id
            addr = self.partner_id.address_get(['delivery'])
            fiscal_position = self.env['account.fiscal.position'].get_fiscal_position(self.partner_id.id, delivery_id=addr['delivery'])

            bank_id = p.bank_ids and p.bank_ids.ids[0] or False

            # If partner has no warning, check its company
            if p.invoice_warn == 'no-message' and p.parent_id:
                p = p.parent_id
            if p.invoice_warn != 'no-message':
                # Block if partner only has warning but parent company is blocked
                if p.invoice_warn != 'block' and p.parent_id and p.parent_id.invoice_warn == 'block':
                    p = p.parent_id
                warning = {
                    'title': _("Warning for %s") % p.name,
                    'message': p.invoice_warn_msg
                    }
                if p.invoice_warn == 'block':
                    self.partner_id = False
                return {'warning': warning}

        self.account_id = account_id
        self.payment_term_id = term_id.id or  payment_term_id
        self.fiscal_position_id = position_id.id or fiscal_position

        if type in ('in_invoice', 'in_refund'):
            self.partner_bank_id = bank_id

    @api.onchange('fiscal_position_id')
    def _onchange_br_account_fiscal_position_id(self):
        if self.fiscal_position_id and self.fiscal_position_id.account_id:
            self.account_id = self.fiscal_position_id.account_id.id
        if not self.fiscal_position_id.account_id:
            self._onchange_partner_id()
        if self.fiscal_position_id and self.fiscal_position_id.journal_id:
            self.journal_id = self.fiscal_position_id.journal_id

        # Correção do erro quando advindo da ordem de compras
        # Assim, da primeira vez ou quando estiver marcado automática
        # a posição fiscal o campo do IPI será preenchido automaticamente.
        if self.purchase_id:
            ol_new_lines = self.purchase_id.order_line
            fpos_id = self.fiscal_position_id.search([('journal_id', '=', self.journal_id.id)])

            # Corrindo a posição fiscal quando vier mais de um id
            # Assim o erro de singleton é afastado.
            if len(fpos_id) >= 1:
                # Adicionada iteração para quando advier a fatura do purchase,
                # A mesma irá processar linha-a-linha afastando o erro de singleton. (JM)
                for pol in ol_new_lines:
                    pol.ipi_cst = fpos_id[0].ipi_tax_rule_ids.cst_ipi
                    self._prepare_invoice_line_from_po_line(pol)

        # Adicionado bloco de exceptions a fim de computar todos CST's e CFOP
        # na invoice do fornecedor e afastar eventuais erros.
        for l in self.invoice_line_ids:

            try:
                if len(self.fiscal_position_id.icms_tax_rule_ids) >= 1:
                    l.cfop_id = self.fiscal_position_id.icms_tax_rule_ids[0].cfop_id.id or False


                if len(self.fiscal_position_id.ipi_tax_rule_ids) >= 1:
                    l.ipi_cst = self.fiscal_position_id.ipi_tax_rule_ids.cst_ipi or False

                if len(self.fiscal_position_id.pis_tax_rule_ids) >= 1:
                    l.pis_cst = self.fiscal_position_id.pis_tax_rule_ids.cst_pis or False

                if len(self.fiscal_position_id.icms_tax_rule_ids) >= 1:
                    l.icms_csosn_simples = self.fiscal_position_id.icms_tax_rule_ids[0].csosn_icms  or \
                            self.fiscal_position_id.simples_tax_rule_ids[0].csosn_icms or False

                if len(self.fiscal_position_id.cofins_tax_rule_ids) >= 1:
                    l.cofins_cst = self.fiscal_position_id.cofins_tax_rule_ids.cst_cofins or False

                if len(self.fiscal_position_id.ii_tax_rule_ids) >= 1:
                    l.ii_rule_id = self.fiscal_position_id.ii_tax_rule_ids.ii_rule_id or False

            except TypeError:
                l.cfop_id = False
                l.ipi_cst = False
                l.pis_cst = False
                l.icms_csosn_simples = False
                l.cofins_cst = False
                l.ii_rule_id = False

            finally:
                if not self.fiscal_position_id:
                    l.cfop_id = False
                    l.ipi_cst = False
                    l.pis_cst = False
                    l.icms_csosn_simples = False
                    l.cofins_cst = False
                    l.ii_rule_id = False

        ob_ids = [x.id for x in self.fiscal_position_id.fiscal_observation_ids]
        self.fiscal_observation_ids = [(6, False, ob_ids)]


    @api.multi
    def action_invoice_open(self):

        if self.type == 'in_invoice':

            ref_purchase_order_origin = self.origin

            if ref_purchase_order_origin:

                for invoice_line in self.invoice_line_ids:

                    if not invoice_line.purchase_line_id:
                        raise UserError ('Did not found a product in purchase order reference. Check invoice products again!!')

                    if invoice_line.quantity > (invoice_line.purchase_line_id.qty_received - (invoice_line.purchase_line_id.qty_invoiced - invoice_line.quantity)):
                        raise UserError ('Quantity is not the same in purchase order reference. Check invoice quantity again!!')

                    if invoice_line.price_unit != invoice_line.purchase_line_id.price_unit:
                        raise UserError ('Price is not the same in purchase order reference. Check invoice price again!!')

        return super(AccountInvoice, self).action_invoice_open()

    @api.multi
    def get_taxes_values(self):
        if len(self.fiscal_position_id.simples_tax_rule_ids) >= 1:
            for l in self.invoice_line_ids:
                l.icms_csosn_simples = self.fiscal_position_id.simples_tax_rule_ids[0].csosn_icms

        return super(AccountInvoice, self).get_taxes_values()

    def _check_nfe_number(self):
        if not self.vendor_number:
            return True
        result = self.env['account.invoice'].search(
            [('partner_id', '=', self.partner_id.id), ('vendor_number', '=', self.vendor_number)])
        if result:
            for i in result:
                if self.id != i.id:
                    return False
        return True

    _constraints = [(_check_nfe_number, 'Esse número de Nota Fiscal já existe para este fornecedor!', [])]