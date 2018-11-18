# -*- coding: utf-8 -*-

import logging

from odoo import SUPERUSER_ID
from odoo.tools.translate import _
from odoo.exceptions import UserError
import odoo.addons.decimal_precision as dp

from odoo import api, models, fields

_logger = logging.getLogger(__name__)


class NewPosOrder(models.Model):
    _inherit = "pos.order"

    discount_total = fields.Float(string='Total Discount(Fixed)', default=0.0)
    discount_percent = fields.Float(string='Total Discount(%)', default=0.0)

    @api.onchange('discount_percent')
    def change_discount_fixed(self):
        if self.discount_percent:
            self.discount_total = 0.0

    @api.onchange('discount_total')
    def change_discount_percent(self):
        if self.discount_total:
            self.discount_percent = 0.0

    @api.depends('statement_ids', 'lines.price_subtotal_incl', 'lines.discount', 'lines.discount_fixed','discount_total','discount_percent', 'amount_total', 'total_discount')
    def _compute_amount_all(self):
        super(NewPosOrder, self)._compute_amount_all()

        for order in self:

            currency = order.pricelist_id.currency_id
            amount_untaxed = currency.round(sum(line.price_subtotal for line in order.lines))

            order.amount_total = order.amount_tax + amount_untaxed
            if order.discount_total > 0:
                if order.amount_total < 0:
                    order.amount_total += order.discount_total
                else:
                    order.amount_total -= order.discount_total
                # for l in order.lines:
                #     # disc_total = order.discount_total / len(order.lines)
                #     # disc_perc = ((l.qty * l.price_unit) * order.discount_percent) / 100
                #     # disc = ((l.qty * l.price_unit) * l.discount) / 100
                #     l.write({'discount_total_by_line': '%.2f' % (order.amount_total)})

            if order.discount_percent > 0:
                if order.amount_total < 0:
                    order.amount_total -= ((order.amount_tax + amount_untaxed) * order.discount_percent / 100)
                else:
                    order.amount_total -= ((order.amount_tax + amount_untaxed) * order.discount_percent / 100)
            order.write({'total':order.amount_total / len(order.lines)})
                # for l in order.lines:
                #     l.write({'discount_percent_by_line':(((l.qty * l.price_unit) * order.discount_percent) / 100)})

    def _order_fields(self, ui_order):
        new_discount = super(NewPosOrder, self)._order_fields(ui_order)
        new_discount['discount_total'] = ui_order['discount_total']
        new_discount['discount_percent'] = ui_order['discount_percent']
        return new_discount

    def test_paid(self):
        """A Point of Sale is paid when the sum
        @return: True
        """
        total = 0
        for order in self:
            value_before_total, value_after_total = str(order.amount_total).split('.')
            value_total = float('.'.join((value_before_total, value_after_total[0:2])))
            if value_total == order.amount_paid:
                return True
            for i in order.lines:
                if i.discount:
                    before_dec, after_dec = str(i.valor_bruto * (1 - (i.discount / 100))).split('.')
                    total += float('.'.join((before_dec, after_dec[0:2])))
                else:
                    total += i.price_subtotal
            if total < 0:
                value_before, value_after = str((total - ((order.discount_percent * total) / 100) + order.discount_total)).split('.')
            else:
                value_before, value_after = str((total - ((order.discount_percent * total) / 100) - order.discount_total)).split('.')
            value = float('.'.join((value_before, value_after[0:2])))
            if order.lines and not order.amount_total:
                continue
            if (not order.lines) or (not order.statement_ids) or (abs(value - order.amount_paid) > 0.01):
                return False
        return True

    def action_invoice(self):

        inv_ref = self.env['account.invoice']
        inv_line_ref = self.env['account.invoice.line']
        product_obj = self.env['product.product']
        inv_ids = []

        for order in self:
            # Force company for all SUPERUSER_ID action
            company_id = order.company_id.id
            if order.invoice_id:
                inv_ids.append(order.invoice_id.id)
                continue

            if not order.partner_id:
                raise UserError(_('Please provide a partner for the sale.'))

            acc = order.partner_id.property_account_receivable_id.id

# =============adding 'discount_total' to invoice================================================================
            inv = {
                'name': order.name,
                'origin': order.name,
                'account_id': acc,
                'journal_id': order.sale_journal.id or None,
                'type': 'out_invoice',
                'reference': order.name,
                'partner_id': order.partner_id.id,
                'comment': order.note or '',
                'currency_id': order.pricelist_id.currency_id.id, # considering partner's sale pricelist's currency
                'company_id': company_id,
                'user_id': self.user_id.id,
                'discount_total': order.discount_total,
                'discount_percent': order.discount_percent,

            }
            invoice = inv_ref.new(inv)
            invoice._onchange_partner_id()
            invoice.fiscal_position_id = order.fiscal_position_id

            inv = invoice._convert_to_write(invoice._cache)
            if not inv.get('account_id', None):
                inv['account_id'] = acc
            inv_id = inv_ref.create(SUPERUSER_ID, inv)

            self.write([order.id], {'invoice_id': inv_id, 'state': 'invoiced'})
            inv_ids.append(inv_id)
            for line in order.lines:
                inv_name = product_obj.name_get([line.product_id.id])[0][1]

# ===============adding 'discount fixed' to invoice lines==========================================
                inv_line = {
                    'invoice_id': inv_id,
                    'product_id': line.product_id.id,
                    'quantity': line.qty,
                    'account_analytic_id': self._prepare_analytic_account(line),
                    'name': inv_name,
                    'discount_fixed': line.discount_fixed,
                }

                #Oldlin trick
                invoice_line = inv_line_ref.new(SUPERUSER_ID, inv_line)
                invoice_line._onchange_product_id()
                invoice_line.invoice_line_tax_ids = [tax.id for tax in invoice_line.invoice_line_tax_ids if tax.company_id.id == company_id]
                fiscal_position_id = line.order_id.fiscal_position_id
                if fiscal_position_id:
                    invoice_line.invoice_line_tax_ids = fiscal_position_id.map_tax(invoice_line.invoice_line_tax_ids)
                invoice_line.invoice_line_tax_ids = [tax.id for tax in invoice_line.invoice_line_tax_ids]
                # We convert a new id object back to a dictionary to write to bridge between old and new api
                inv_line = invoice_line._convert_to_write(invoice_line._cache)
                inv_line.update(price_unit=line.price_unit, discount=line.discount, discount_fixed=line.discount_fixed)
                inv_line_ref.create(SUPERUSER_ID, inv_line)
            inv_ref.compute_taxes(SUPERUSER_ID, [inv_id])
            self.signal_workflow([order.id], 'invoice')
            inv_ref.signal_workflow(SUPERUSER_ID, [inv_id], 'validate')

        if not inv_ids: return {}

        mod_obj = self.env['ir.model.data']
        res = mod_obj.get_object_reference('account', 'invoice_form')
        res_id = res and res[1] or False
        return {
            'name': _('Customer Invoice'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': [res_id],
            'res_model': 'account.invoice',
            'context': "{'type':'out_invoice'}",
            'type': 'ir.actions.act_window',
            'target': 'current',
            'res_id': inv_ids and inv_ids[0] or False,
        }

    # def _create_account_move_line(self, session=None, move_id=None):
    #     # Tricky, via the workflow, we only have one id in the ids variable
    #     """Create a account move line of order grouped by products or not."""
    #     account_move_obj = self.env['account.move']
    #     account_tax_obj = self.env['account.tax']
    #     property_obj = self.env['ir.property']
    #     cur_obj = self.env['res.currency']
    #
    #     # session_ids = set(order.session_id for order in self.browse(cr, uid, ids, context=context))
    #
    #     if session and not all(session.id == order.session_id.id for order in self):
    #         raise UserError(_('Selected orders do not have the same session!'))
    #
    #     grouped_data = {}
    #     have_to_group_by = session and session.config_id.group_by or False
    #     rounding_method = session and session.config_id.company_id.tax_calculation_rounding_method
    #
    #     for order in self:
    #         if order.account_move:
    #             continue
    #         if order.state != 'paid':
    #             continue
    #
    #         current_company = order.sale_journal.company_id
    #
    #         group_tax = {}
    #         account_def = property_obj.get('property_account_receivable_id', 'res.partner')
    #
    #         order_account = order.partner_id and \
    #                         order.partner_id.property_account_receivable_id and \
    #                         order.partner_id.property_account_receivable_id.id or \
    #                         account_def and account_def.id
    #
    #         if move_id is None:
    #             # Create an entry for the sale
    #             # FORWARD-PORT UP TO SAAS-12
    #             journal_id = self.pool['ir.config_parameter'].get_param(SUPERUSER_ID,
    #                                                                     'pos.closing.journal_id_%s' % (
    #                                                                     current_company.id),
    #                                                                     default=order.sale_journal.id)
    #             move_id = self._create_account_move(order.session_id.start_at, order.name, int(journal_id),
    #                                                 order.company_id.id)
    #
    #         move = account_move_obj.browse(SUPERUSER_ID, move_id)
    #
    #         def insert_data(data_type, values):
    #             # if have_to_group_by:
    #
    #             # 'quantity': line.qty,
    #             # 'product_id': line.product_id.id,
    #             values.update({
    #                 'partner_id': order.partner_id and self.env["res.partner"]._find_accounting_partner(
    #                     order.partner_id).id or False,
    #                 'move_id': move_id,
    #             })
    #
    #             if data_type == 'product':
    #                 key = ('product', values['partner_id'],
    #                        (values['product_id'], tuple(values['tax_ids'][0][2]), values['name']),
    #                        values['analytic_account_id'], values['debit'] > 0)
    #             elif data_type == 'tax':
    #                 key = ('tax', values['partner_id'], values['tax_line_id'], values['debit'] > 0)
    #             elif data_type == 'counter_part':
    #                 key = ('counter_part', values['partner_id'], values['account_id'], values['debit'] > 0)
    #             else:
    #                 return
    #
    #             grouped_data.setdefault(key, [])
    #
    #             # if not have_to_group_by or (not grouped_data[key]):
    #             #     grouped_data[key].append(values)
    #             # else:
    #             #     pass
    #
    #             if have_to_group_by:
    #                 if not grouped_data[key]:
    #                     grouped_data[key].append(values)
    #                 else:
    #                     for line in grouped_data[key]:
    #                         if line.get('tax_code_id') == values.get('tax_code_id'):
    #                             current_value = line
    #                             current_value['quantity'] = current_value.get('quantity', 0.0) + values.get(
    #                                 'quantity', 0.0)
    #                             current_value['credit'] = current_value.get('credit', 0.0) + values.get('credit',
    #                                                                                                     0.0)
    #                             current_value['debit'] = current_value.get('debit', 0.0) + values.get('debit', 0.0)
    #                             break
    #                     else:
    #                         grouped_data[key].append(values)
    #             else:
    #                 grouped_data[key].append(values)
    #
    #         # because of the weird way the pos order is written, we need to make sure there is at least one line,
    #         # because just after the 'for' loop there are references to 'line' and 'income_account' variables (that
    #         # are set inside the for loop)
    #         # TOFIX: a deep refactoring of this method (and class!) is needed in order to get rid of this stupid hack
    #         assert order.lines, _('The POS order must have lines when calling this method')
    #         # Create an move for each order line
    #
    #         cur = order.pricelist_id.currency_id
    #         for line in order.lines:
    #             amount = line.price_subtotal
    #
    #             # Search for the income account
    #             if line.product_id.property_account_income_id.id:
    #                 income_account = line.product_id.property_account_income_id.id
    #             elif line.product_id.categ_id.property_account_income_categ_id.id:
    #                 income_account = line.product_id.categ_id.property_account_income_categ_id.id
    #             else:
    #                 raise UserError(_('Please define income ' \
    #                                   'account for this product: "%s" (id:%d).') \
    #                                 % (line.product_id.name, line.product_id.id))
    #
    #             name = line.product_id.name
    #             if line.notice:
    #                 # add discount reason in move
    #                 name = name + ' (' + line.notice + ')'
    #
    #             # Create a move for the line for the order line
    #             insert_data('product', {
    #                 'name': name,
    #                 'quantity': line.qty,
    #                 'product_id': line.product_id.id,
    #                 'account_id': income_account,
    #                 'analytic_account_id': self._prepare_analytic_account(line),
    #                 'credit': ((amount > 0) and amount) or 0.0,
    #                 'debit': ((amount < 0) and -amount) or 0.0,
    #                 'tax_ids': [(6, 0, line.tax_ids_after_fiscal_position.ids)],
    #                 'partner_id': order.partner_id and self.pool.get("res.partner")._find_accounting_partner(
    #                     order.partner_id).id or False
    #             })
    #
    #             # Create the tax lines
    #             taxes = []
    #             for t in line.tax_ids_after_fiscal_position:
    #                 if t.company_id.id == current_company.id:
    #                     taxes.append(t.id)
    #             if not taxes:
    #                 continue
    #             for tax in account_tax_obj.browse(taxes).compute_all(
    #                                     line.price_unit * (100.0 - line.discount) / 100.0, cur, line.qty)['taxes']:
    #                 insert_data('tax', {
    #                     'name': _('Tax') + ' ' + tax['name'],
    #                     'product_id': line.product_id.id,
    #                     'quantity': line.qty,
    #                     'account_id': tax['account_id'] or income_account,
    #                     'credit': ((tax['amount'] > 0) and tax['amount']) or 0.0,
    #                     'debit': ((tax['amount'] < 0) and -tax['amount']) or 0.0,
    #                     'tax_line_id': tax['id'],
    #                     'partner_id': order.partner_id and self.pool.get("res.partner")._find_accounting_partner(
    #                         order.partner_id).id or False
    #                 })
    #
    #         # round tax lines per order
    #         if rounding_method == 'round_globally':
    #             for group_key, group_value in grouped_data.iteritems():
    #                 if group_key[0] == 'tax':
    #                     for line in group_value:
    #                         line['credit'] = cur.round(line['credit'])
    #                         line['debit'] = cur.round(line['debit'])
    #
    #         if order.discount_total:
    #             insert_data('counter_part', {
    #                 'name': 'Discount',
    #                 'account_id': order.session_id.config_id.discount_account.id,
    #                 'credit': ((order.discount_total < 0) and -order.discount_total) or 0.0,
    #                 'debit': ((order.discount_total > 0) and order.discount_total) or 0.0,
    #                 'partner_id': order.partner_id and self.pool.get("res.partner")._find_accounting_partner(
    #                     order.partner_id).id or False
    #             })
    #         elif order.discount_percent:
    #             discount = (100 * order.amount_total) / (100 - order.discount_percent)
    #             discount -= order.amount_total
    #             print discount, "--------------"
    #             insert_data('counter_part', {
    #                 'name': 'Discount',
    #                 'account_id': order.session_id.config_id.discount_account.id,
    #                 'credit': ((discount < 0) and -discount) or 0.0,
    #                 'debit': ((discount > 0) and discount) or 0.0,
    #                 'partner_id': order.partner_id and self.pool.get("res.partner")._find_accounting_partner(
    #                     order.partner_id).id or False
    #             })
    #         # counterpart
    #         insert_data('counter_part', {
    #             'name': _("Trade Receivables"),  # order.name,
    #             'account_id': order_account,
    #             'credit': ((order.amount_total < 0) and -order.amount_total) or 0.0,
    #             'debit': ((order.amount_total > 0) and order.amount_total) or 0.0,
    #             'partner_id': order.partner_id and self.pool.get("res.partner")._find_accounting_partner(
    #                 order.partner_id).id or False
    #         })
    #
    #         order.write({'state': 'done', 'account_move': move_id})
    #
    #     all_lines = []
    #     for group_key, group_data in grouped_data.iteritems():
    #         for value in group_data:
    #             all_lines.append((0, 0, value), )
    #     if move_id:  # In case no order was changed
    #         self.pool.get("account.move").write(SUPERUSER_ID, [move_id], {'line_ids': all_lines})
    #         self.pool.get("account.move").post(SUPERUSER_ID, [move_id])
    #
    #     return True


class NewPosLines(models.Model):
    _inherit = "pos.order.line"

    price_unit = fields.Float(string='Unit Price', digits=0)
    qty = fields.Float('Quantity', digits_compute=dp.get_precision('Product Unit of Measure'))
    discount_fixed = fields.Float('Discount Fixed', default=0.0)
    discountStr = fields.Char('discountStr')


    @api.onchange('discount_fixed')
    def change_discount_fixed_line(self):
        if self.discount_fixed:
            self.discount = 0.0

    @api.onchange('discount')
    def change_discount_line(self):
        if self.discount:
            self.discount_fixed = 0.0

    @api.onchange('qty')
    def change_qty_line(self):
        self._compute_amount_line_all()

    @api.onchange('price_unit')
    def change_price_unit_line(self):
        self._compute_amount_line_all()

    @api.depends('price_unit', 'tax_ids', 'qty', 'discount', 'discount_fixed', 'product_id')
    def _compute_amount_line_all(self):
        for line in self:
            currency = line.order_id.pricelist_id.currency_id
            taxes = line.tax_ids.filtered(lambda tax: tax.company_id.id == line.order_id.company_id.id)
            fiscal_position_id = line.order_id.fiscal_position_id
            if fiscal_position_id:
                taxes = fiscal_position_id.map_tax(taxes)
# =============== finding subtotal for each orderline=========================================================
            line.valor_desconto = (line.valor_bruto * line.discount / 100) + line.discount_fixed
            if line.discount_fixed != 0:
                price = line.price_unit
                if line.qty < 0:
                    line.price_subtotal = line.price_subtotal_incl = price * line.qty + line.discount_fixed
                else:
                    line.price_subtotal = line.price_subtotal_incl = price * line.qty - line.discount_fixed
            else:
                price = line.price_unit
                #disc = "%.2f" % (price * line.qty * (line.discount or 0.0) / 100)
                #disc = (price * line.qty) * (line.discount or 0.0) / 100
                #price_u = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                before_dec, after_dec = str((line.price_unit * (1 - (line.discount or 0.0) / 100.0))).split('.')
                price_u = float('.'.join((before_dec, after_dec[0:2])))
                line.price_subtotal = line.price_subtotal_incl = '%.2f' % (price_u * line.qty)
            if taxes:
                taxes = taxes.compute_all(price, currency, line.qty, product=line.product_id, partner=line.order_id.partner_id or False)
                line.price_subtotal = taxes['total_excluded']
                line.price_subtotal_incl = taxes['total_included']
            line.price_subtotal = currency.round(line.price_subtotal)
            line.price_subtotal_incl = currency.round(line.price_subtotal_incl)


class AccountMoveLineExtra(models.Model):
    _inherit = 'account.move.line'

    _sql_constraints = [
        ('credit_debit1', 'CHECK (credit*debit=0)', 'Wrong credit or debit value in accounting entry !'),
        ('credit_debit2', 'CHECK (credit*debit=0)', 'Wrong credit or debit value in accounting entry !'),
    ]

    @api.multi
    def _update_check(self):
        """ This module is overwritten, to avoid the warning raised when we edit the journal entries"""
        move_ids = set()
        for line in self:
            err_msg = _('Move name (id): %s (%s)') % (line.move_id.name, str(line.move_id.id))
            if line.move_id.id not in move_ids:
                move_ids.add(line.move_id.id)
            self.env['account.move'].browse(list(move_ids))._check_lock_date()
        return True

    @api.multi
    def reconcile(self, writeoff_acc_id=False, writeoff_journal_id=False):
        """ This function is overwritten to remove some warnings"""
        # Perform all checks on lines
        company_ids = set()
        all_accounts = []
        partners = set()
        for line in self:
            company_ids.add(line.company_id.id)
            all_accounts.append(line.account_id)
            if (line.account_id.internal_type in ('receivable', 'payable')):
                partners.add(line.partner_id.id)
            if line.reconciled:
                raise UserError(_('You are trying to reconcile some entries that are already reconciled!'))
        if len(company_ids) > 1:
            raise UserError(_('To reconcile the entries company should be the same for all entries!'))
        if not all_accounts[0].reconcile:
            raise UserError(_('The account %s (%s) is not marked as reconciliable !') % (
            all_accounts[0].name, all_accounts[0].code))
        # reconcile everything that can be
        remaining_moves = self.auto_reconcile_lines()

        # if writeoff_acc_id specified, then create write-off move with value the remaining amount from move in self
        if writeoff_acc_id and writeoff_journal_id and remaining_moves:
            all_aml_share_same_currency = all([x.currency_id == self[0].currency_id for x in self])
            writeoff_vals = {
                'account_id': writeoff_acc_id.id,
                'journal_id': writeoff_journal_id.id
            }
            if not all_aml_share_same_currency:
                writeoff_vals['amount_currency'] = False
            writeoff_to_reconcile = remaining_moves._create_writeoff(writeoff_vals)
            # add writeoff line to reconcile algo and finish the reconciliation
            remaining_moves = (remaining_moves + writeoff_to_reconcile).auto_reconcile_lines()
            return writeoff_to_reconcile
        return True


class AccountMoveNew(models.Model):
    _inherit = 'account.move'

    @api.multi
    def assert_balanced(self):
        """Overwritten to remove the warning raised.(For editing the journal entry)"""
        if not self.ids:
            return True
        prec = self.env['decimal.precision'].precision_get('Account')

        self._cr.execute("""\
                SELECT      move_id
                FROM        account_move_line
                WHERE       move_id in %s
                GROUP BY    move_id
                HAVING      abs(sum(debit) - sum(credit)) > %s
                """, (tuple(self.ids), 10 ** (-max(5, prec))))

        # Avoiding validation of unbalanced journal entry (send and post).
        if len(self._cr.fetchall()) != 0:
            if len(self._cr.fetchall()) > 0:
                raise UserError(_("Cannot create unbalanced journal entry. ids - %s" % (str(self.ids))))

        return True












