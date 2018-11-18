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

from odoo import api, fields, models, tools, _
from random import SystemRandom
from odoo.exceptions import UserError
import psycopg2
import logging
from odoo.http import request
from datetime import datetime, timedelta
from escpos.serial import SerialSettings
from escpos.network import NetworkConnection


_logger = logging.getLogger(__name__)


class PosMakePayment(models.TransientModel):
    _inherit = 'pos.make.payment'

    refund_id = fields.Many2one('pos.order', string='Refund ID')
    journal_id = fields.Many2one('account.journal', string='Payment Mode', required=True, default=False)


class PosSession(models.Model):
    _inherit = 'pos.session'

    def _check_pos_manager(self):
        user = self.env['res.users'].sudo().browse(self._uid)
        for i in self:
            if user.pos_manager:
                i.user_pos_manager = True
            else:
                i.user_pos_manager = False
        return True

    def _compute_sales_total(self):
        for j in self:
            sales = self.env['pos.order'].sudo().search([('session_id','=',j.id)])
            total = 0
            for i in sales:
                total += i.amount_total
            j.sales_total = total

    declared_value = fields.Boolean('Declared Value')
    user_pos_manager = fields.Boolean('Declared Value', compute='_check_pos_manager')
    user_closed = fields.Many2one('res.users','User Closed Session', default=False)
    sales_total = fields.Float('Sales Total', compute='_compute_sales_total')
    note = fields.Text(string='Note')

    @api.multi
    def action_pos_session_closing_control(self):
        user = self.env['res.users'].sudo().browse(self._uid)
        for session in self:
            if not user.pos_manager:
                for i in session.statement_ids:
                    if i.value_difference_box != 0 and i.state != 'confirm':
                        raise UserError(_(u'Diferença no valor de (%s) - Não é possivel fechar caixa com alguma diferença!' % (i.journal_id.name)))
            #DO NOT FORWARD-PORT
            if session.state == 'closing_control':
                session.action_pos_session_close()
                continue
            for statement in session.statement_ids:
                if (statement != session.cash_register_id) and (statement.balance_end != statement.balance_end_real):
                    statement.write({'balance_end_real': statement.balance_end})
            session.write({'state': 'closing_control', 'stop_at': fields.Datetime.now()})
            if not session.config_id.cash_control:
                session.action_pos_session_close()


    @api.multi
    def action_pos_session_close(self):
        # Close CashBox
        for session in self:
            company_id = session.config_id.company_id.id
            ctx = dict(self.env.context, force_company=company_id, company_id=company_id)
            for st in session.statement_ids:
                if abs(st.difference) > st.journal_id.amount_authorized_diff:
                    # The pos manager can close statements with maximums.
                    if not self.env['ir.model.access'].check_groups("point_of_sale.group_pos_manager"):
                        raise UserError(_("Your ending balance is too different from the theoretical cash closing (%.2f), the maximum allowed is: %.2f. You can contact your manager to force it.") % (st.difference, st.journal_id.amount_authorized_diff))
                if (st.journal_id.type not in ['bank', 'cash']):
                    raise UserError(_("The type of the journal for your payment method should be bank or cash "))
                st.with_context(ctx).sudo().button_confirm_bank()
        self.with_context(ctx)._confirm_orders()
        self.write({'state': 'closed', 'user_closed':self._uid})
        return {
            'type': 'ir.actions.client',
            'name': 'Point of Sale Menu',
            'tag': 'reload',
            'params': {'menu_id': self.env.ref('point_of_sale.menu_point_root').id},
        }

    def change_value_declared(self):
        validate_id = self.env['payment.validate.pos'].create({'session_id':self.id})
        for i in self.statement_ids:
            self.env['payment.validate.line.pos'].create(
                {
                    'journal_id': i.journal_id.id,
                    'payment_validate':validate_id.id
                }
            )
        return {
            'name': _('Session'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'payment.validate.pos',
            'res_id': validate_id.id,
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target':'new'
        }


class PosOrder(models.Model):
    _inherit = "pos.order"

    @api.depends('statement_ids', 'lines.price_subtotal_incl', 'lines.discount')
    def _compute_amount_all(self):

        res = super(PosOrder, self)._compute_amount_all()

        disc_total = 0.0
        for order in self:

            currency = order.pricelist_id.currency_id
            order.amount_untaxed = currency.round(sum(line.price_subtotal for line in order.lines))

            for product in order.lines:
                if product.discount > 0.0:
                    disc_total += (product.qty * product.price_unit) * (product.discount/100)
                if product.discount_fixed > 0.0:
                    disc_total += product.discount_fixed

            if order.discount_percent > 0.0:
                disc_total += order.amount_untaxed * (order.discount_percent/100)

            if order.discount_total > 0.0:
                disc_total += order.discount_total

            order.total_discount = disc_total
            order.amountx_totalx = order.amount_total
        return res

    refund_id = fields.Many2one('pos.order', string='Refund ID')
    authorizer_user_id = fields.Many2one('res.users', string=u'Authorizer User',readonly=True)
    cpf_nfse = fields.Char("CPF", help="CPF do cliente")
    chave_cfe = fields.Char(u"Chave CFe")
    num_sessao_cfe = fields.Char(u"Número de Sessão")
    log_sat = fields.One2many('pos.order.log','pos_order_id', u"Log Sat")
    xml_cfe_retorn = fields.Text(u"XML Retorno")
    xml_cfe_cancel = fields.Text(u"XML Cancel")
    chave_cfe_can = fields.Char(u"Chave CFe Cancelamento")
    amount_untaxed = fields.Float(string='Subtotal', compute=_compute_amount_all, digits=0)
    number_installments = fields.Integer(string='number_installments', default=1)
    total_discount = fields.Float(string='Total Discount', compute=_compute_amount_all, digits=0)
    spending_point_loyalty = fields.Float(string='Spending Points')
    points_won = fields.Float(string='Pontos Ganhos')
    points_spend = fields.Float(string='Pontos Gastos')
    statement_ids = fields.One2many('account.bank.statement.line', 'pos_statement_id', string='Payments', readonly=False)
    amountx_totalx = fields.Float(string='Total Price')
    total = fields.Float('Total')


    def _init_printer(self):

        if self.impressora == 'epson-tm-t20':
            _logger.info(u'SAT Impressao: Epson TM-T20')
            from escpos.impl.epson import TMT20 as Printer
        elif self.impressora == 'bematech-mp4200th':
            _logger.info(u'SAT Impressao: Bematech MP4200TH')
            from escpos.impl.bematech import MP4200TH as Printer
        elif self.impressora == 'daruma-dr700':
            _logger.info(u'SAT Impressao: Daruma Dr700')
            from escpos.impl.daruma import DR700 as Printer
        elif self.impressora == 'elgin-i9':
            _logger.info(u'SAT Impressao: Elgin I9')
            from escpos.impl.elgin import ElginI9 as Printer
        else:
            self.printer = False

        if self.print_connection == 'network':
            conn = NetworkConnection.create(self.printer_params)
            self.conn = conn
        else:
            conn = SerialSettings.as_from(
                self.printer_params).get_connection()

        printer = Printer(conn)
        printer.init()

        return printer

    @api.multi
    def refund(self):
        """Create a copy of order  for refund order"""
        PosOrder = self.env['pos.order']
        current_session = self.env['pos.session'].search([('state', '!=', 'closed'), ('user_id', '=', self.env.uid)], limit=1)
        if not current_session:
            raise UserError(_('To return product(s), you need to open a session that will be used to register the refund.'))
        for order in self:
            refunds = self.search([('refund_id','=',order.id)], limit=1)
            if refunds:
                raise UserError(_('Pedido ja devolvido anteriormente - %s !' % refunds.name))
            clone = order.copy({
                # ot used, name forced by create
                'name': order.name + _(' REFUND'),
                'session_id': current_session.id,
                'date_order': fields.Datetime.now(),
                'pos_reference': order.pos_reference,
                'refund_id': order.id
            })
            PosOrder += clone
            if order.partner_id and order.loyalty_points != 0:
                order.partner_id.write({'loyalty_points': order.partner_id.loyalty_points - order.loyalty_points})
        for clone in PosOrder:
            for order_line in clone.lines:
                order_line.write({'qty': -order_line.qty})
        return {
            'name': _('Return Products'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'pos.order',
            'res_id': PosOrder.ids[0],
            'view_id': False,
            'context': self.env.context,
            'type': 'ir.actions.act_window',
            'target': 'current',
        }

    @api.model
    def print_receipt_tef(self, cupom_cliente,cupom_est,config):

        self.print_connection = config['print_connection']
        self.impressora = config['model_printer_sat']
        self.printer_params = config['parameters_print_sat']

        try:
            printer = self._init_printer()
        except Exception, e:
            _logger.error(e)
            return {'result': False}

        t = 1
        while t == 1:
            try:
                text_cliente = cupom_cliente.split('</br>')
                for i in text_cliente:
                    printer.text(i.encode('utf-8'))
                printer.cut()
                text_est = cupom_est.split('</br>')
                for i in text_est:
                    printer.text(i.encode('utf-8') + '')
                valida = {'result': True}
                printer.cut()
                printer = self._init_printer()
                t = 2
            except Exception, e:
                t = 1
        # self.conn.release()
        return valida

    def reprint_received_tef(self):

        config = self.session_id.config_id

        self.print_connection = config.print_connection
        self.impressora = config.model_printer_sat
        self.printer_params = config.parameters_print_sat

        try:
            printer = self._init_printer()
        except Exception, e:
            _logger.error(e)
            raise UserError(_(u'No Printer Connection!'))
        t = 1
        while t == 1:
            try:
                for statement_line in self.statement_ids:

                    cupom_cliente = statement_line.return_tef_client
                    cupom_est = statement_line.return_tef_establishment

                    text_cliente = cupom_cliente.split('</br>')
                    for i in text_cliente:
                        printer.text(i.encode('utf-8'))
                    printer.cut()
                    text_est = cupom_est.split('</br>')
                    for i in text_est:
                        printer.text(i.encode('utf-8') + '')
                    valida = {'result': True}
                    printer.cut()
                    printer = self._init_printer()
                t = 2
            except Exception, e:
                t = 1
        # self.conn.release()
        return valida

    def _payment_fields(self, ui_paymentline):
        return {
            'amount':       ui_paymentline['amount'] or 0.0,
            'payment_date': ui_paymentline['name'],
            'statement_id': ui_paymentline['statement_id'],
            'payment_name': ui_paymentline.get('note', False),
            'journal':      ui_paymentline['journal_id'],
            'number_card':  'number_card' in ui_paymentline and ui_paymentline['number_card'] or '',
            'authorization_number': 'authorization_number' in ui_paymentline and ui_paymentline['authorization_number'] or '',
            'card_banner': 'card_banner' in ui_paymentline and ui_paymentline['card_banner'] or '',
            'number_installment': 'number_installment' in ui_paymentline and ui_paymentline['number_installment'] or '',
            'return_tef_reduced': 'return_tef_reduced' in ui_paymentline and ui_paymentline['return_tef_reduced'] or '',
            'return_tef_client': 'return_tef_client' in ui_paymentline and ui_paymentline['return_tef_client'] or '',
            'return_tef_cancel': 'return_tef_cancel' in ui_paymentline and ui_paymentline['return_tef_cancel'] or '',
            'return_tef_establishment': 'return_tef_establishment' in ui_paymentline and ui_paymentline['return_tef_establishment'] or '',
        }

    def add_payment(self, data):
        """Create a new payment for the order"""
        args = {
            'amount': 'amount' in data and data['amount'] or '',
            'date': 'payment_date' in data and data.get('payment_date', fields.Date.today()) or '',
            'name': 'payment_name' in data and self.name + ': ' + (data.get('payment_name', '') or '') or '',
            'partner_id': self.env["res.partner"]._find_accounting_partner(self.partner_id).id or False,
            'number_card': 'number_card' in data and data['number_card'] or '',
            'flag_card': 'card_banner' in data and data['card_banner'] or '',
            'number_installments': 'number_installment' in data and data['number_installment'] or '1',
            'authorization_number': 'authorization_number' in data and data['authorization_number'] or '',
            'return_tef_reduced': 'return_tef_reduced' in data and data['return_tef_reduced'] or '',
            'return_tef_client': 'return_tef_client' in data and data['return_tef_client'] or '',
            'return_tef_cancel': 'return_tef_cancel' in data and data['return_tef_cancel'] or '',
            'return_tef_establishment': 'return_tef_establishment' in data and data['return_tef_establishment'] or '',
        }

        type_collection = ''
        session = self.session_id
        journal_id = data.get('journal', False)
        statement_id = data.get('statement_id', False)
        assert journal_id or statement_id, "No statement_id or journal_id passed to the method!"

        journal = self.env['account.journal'].browse(journal_id)
        # use the company of the journal and not of the current user
        company_cxt = dict(self.env.context, force_company=journal.company_id.id)
        account_def = session.config_id.default_account_id.id or self.env['ir.property'].with_context(company_cxt).get('property_account_receivable_id', 'res.partner')
        args['account_id'] = account_def or (self.partner_id.property_account_receivable_id.id) or False

        if not args['account_id']:
            if not args['partner_id']:
                msg = _('There is no receivable account defined to make payment.')
            else:
                msg = _('There is no receivable account defined to make payment for the partner: "%s" (id:%d).') % (
                    self.partner_id.name, self.partner_id.id,)
            raise UserError(msg)

        context = dict(self.env.context)
        context.pop('pos_session_id', False)
        for statement in self.session_id.statement_ids:
            if statement.id == statement_id:
                journal_id = statement.journal_id.id
                break
            elif statement.journal_id.id == journal_id:
                statement_id = statement.id
                break
        if not statement_id:
            raise UserError(_('You have to open at least one cashbox.'))

        if 'card_banner' in data and data['card_banner']:

            if statement.journal_id.sat_payment_mode == '04':
                type_collection = 'debit'
            elif statement.journal_id.sat_payment_mode == '03':
                type_collection = 'credit'

            card_banner = data.get('card_banner', False)
            src_card_banner = self.env['card.banner'].search([('name', '=', card_banner)])

            if src_card_banner.journal_id:

                journal_id = src_card_banner.journal_id.id

        elif statement.journal_id.banner_name:

            if statement.journal_id.sat_payment_mode == '04':
                type_collection = 'debit'
            elif statement.journal_id.sat_payment_mode == '03':
                type_collection = 'credit'

            src_card_banner = self.env['card.banner'].search([('name', '=', statement.journal_id.banner_name)])

            args['flag_card'] = statement.journal_id.banner_name

            if src_card_banner.journal_id:

                journal_id = src_card_banner.journal_id.id

        args.update({
            'type_collection': type_collection,
            'statement_id': statement_id,
            'pos_statement_id': self.id,
            'journal_id': journal_id,
            'ref': self.session_id.name,
        })

        account_bank_statement_line = self.env['account.bank.statement.line'].create(args)
        account_bank_statement_line.write({'journal_id': journal_id})

        return statement_id

    def _create_account_move_line(self, session=None, move=None):
        # Tricky, via the workflow, we only have one id in the ids variable
        """Create a account move line of order grouped by products or not."""
        IrProperty = self.env['ir.property']
        ResPartner = self.env['res.partner']

        if session and not all(session.id == order.session_id.id for order in self):
            raise UserError(_('Selected orders do not have the same session!'))

        grouped_data = {}
        have_to_group_by = session and session.config_id.group_by or False

        for order in self.filtered(lambda o: not o.account_move or order.state == 'paid'):
            current_company = order.sale_journal.company_id
            account_def = IrProperty.get(
                'property_account_receivable_id', 'res.partner')
            order_account = session.config_id.default_account_id.id or order.partner_id.property_account_receivable_id.id or account_def and account_def.id
            partner_id = ResPartner._find_accounting_partner(order.partner_id).id or False
            if move is None:
                # Create an entry for the sale
                journal_id = self.env['ir.config_parameter'].sudo().get_param(
                    'pos.closing.journal_id_%s' % current_company.id, default=order.sale_journal.id)
                move = self._create_account_move(
                    order.session_id.start_at, order.name, int(journal_id), order.company_id.id)

            def insert_data(data_type, values):
                # if have_to_group_by:
                values.update({
                    'partner_id': partner_id,
                    'move_id': move.id,
                })

                if data_type == 'product':
                    key = ('product', values['partner_id'], (values['product_id'], tuple(values['tax_ids'][0][2]), values['name']), values['analytic_account_id'], values['debit'] > 0)
                elif data_type == 'tax':
                    key = ('tax', values['partner_id'], values['tax_line_id'], values['debit'] > 0)
                elif data_type == 'counter_part':
                    key = ('counter_part', values['partner_id'], values['account_id'], values['debit'] > 0)
                else:
                    return

                grouped_data.setdefault(key, [])

                if have_to_group_by:
                    if not grouped_data[key]:
                        grouped_data[key].append(values)
                    else:
                        current_value = grouped_data[key][0]
                        current_value['quantity'] = current_value.get('quantity', 0.0) + values.get('quantity', 0.0)
                        current_value['credit'] = current_value.get('credit', 0.0) + values.get('credit', 0.0)
                        current_value['debit'] = current_value.get('debit', 0.0) + values.get('debit', 0.0)
                else:
                    grouped_data[key].append(values)

            # because of the weird way the pos order is written, we need to make sure there is at least one line,
            # because just after the 'for' loop there are references to 'line' and 'income_account' variables (that
            # are set inside the for loop)
            # TOFIX: a deep refactoring of this method (and class!) is needed
            # in order to get rid of this stupid hack
            assert order.lines, _('The POS order must have lines when calling this method')
            # Create an move for each order line
            cur = order.pricelist_id.currency_id
            for line in order.lines:
                amount = line.price_subtotal

                # Search for the income account
                if line.product_id.property_account_income_id.id:
                    income_account = line.product_id.property_account_income_id.id
                elif line.product_id.categ_id.property_account_income_categ_id.id:
                    income_account = line.product_id.categ_id.property_account_income_categ_id.id
                else:
                    raise UserError(_('Please define income '
                                      'account for this product: "%s" (id:%d).')
                                    % (line.product_id.name, line.product_id.id))

                name = line.product_id.name
                if line.notice:
                    # add discount reason in move
                    name = name + ' (' + line.notice + ')'

                # Create a move for the line for the order line
                insert_data('product', {
                    'name': name,
                    'quantity': line.qty,
                    'product_id': line.product_id.id,
                    'account_id': income_account,
                    'analytic_account_id': self._prepare_analytic_account(line),
                    'credit': ((amount > 0) and amount) or 0.0,
                    'debit': ((amount < 0) and -amount) or 0.0,
                    'tax_ids': [(6, 0, line.tax_ids_after_fiscal_position.ids)],
                    'partner_id': partner_id
                })

                # Create the tax lines
                taxes = line.tax_ids_after_fiscal_position.filtered(lambda t: t.company_id.id == current_company.id)
                if not taxes:
                    continue
                for tax in taxes.compute_all(line.price_unit * (100.0 - line.discount) / 100.0, cur, line.qty)['taxes']:
                    insert_data('tax', {
                        'name': _('Tax') + ' ' + tax['name'],
                        'product_id': line.product_id.id,
                        'quantity': line.qty,
                        'account_id': tax['account_id'] or income_account,
                        'credit': ((tax['amount'] > 0) and tax['amount']) or 0.0,
                        'debit': ((tax['amount'] < 0) and -tax['amount']) or 0.0,
                        'tax_line_id': tax['id'],
                        'partner_id': partner_id
                    })

            # counterpart
            insert_data('counter_part', {
                'name': _("Trade Receivables"),  # order.name,
                'account_id': order_account,
                'credit': ((order.amount_total < 0) and -order.amount_total) or 0.0,
                'debit': ((order.amount_total > 0) and order.amount_total) or 0.0,
                'partner_id': partner_id
            })

            if order.discount_total:
                insert_data('counter_part', {
                    'name': 'Discount',
                    'account_id': order.session_id.config_id.discount_account.id,
                    'credit': ((order.discount_total < 0) and -order.discount_total) or 0.0,
                    'debit': ((order.discount_total > 0) and order.discount_total) or 0.0,
                    'partner_id': order.partner_id and self.env["res.partner"]._find_accounting_partner(
                        order.partner_id).id or False
                })

            elif order.discount_percent:
                discount = (100 * order.amount_total) / (100 - order.discount_percent)
                discount -= order.amount_total
                # print discount, "--------------"
                insert_data('counter_part', {
                    'name': 'Discount',
                    'account_id': order.session_id.config_id.discount_account.id,
                    'credit': ((discount < 0) and -discount) or 0.0,
                    'debit': ((discount > 0) and discount) or 0.0,
                    'partner_id': order.partner_id and self.env["res.partner"]._find_accounting_partner(
                        order.partner_id).id or False
                })

            order.write({'state': 'done', 'account_move': move.id})

        all_lines = []
        for group_key, group_data in grouped_data.iteritems():
            for value in group_data:
                all_lines.append((0, 0, value),)
        if move:  # In case no order was changed
            move.sudo().write({'line_ids': all_lines})
            move.sudo().post()
        return True

    @api.model
    def cancel_cupom_sat(self, chave, session_id):
        if not 'CFe' in chave:
            chave = 'CFe' + chave
        res = self.search([('chave_cfe','=',chave)])
        if res:
            config_pos = self.env['pos.session'].browse(session_id).config_id
            conf_sat = self.env['hw.sat'].create_cfe_sat(config_pos.active_code_sat,
                                                    config_pos.library_path_sat,
                                                    config_pos.model_printer_sat,
                                                    config_pos.parameters_print_sat,
                                                    config_pos.sign_ac_sat,
                                                    config_pos.info_sat or '',
                                                    config_pos.print_connection,
                                                    res, 'cancel',chave)
            return {'result':True}
        else:
            res_extra = self.search([('id','=',1)])
            if res_extra:
                config_pos = self.env['pos.session'].browse(session_id).config_id
                conf_sat = self.env['hw.sat'].create_cfe_sat(config_pos.active_code_sat,
                                                             config_pos.library_path_sat,
                                                             config_pos.model_printer_sat,
                                                             config_pos.parameters_print_sat,
                                                             config_pos.sign_ac_sat,
                                                             config_pos.info_sat or '',
                                                             config_pos.print_connection,
                                                             res_extra, 'cancel',chave)
                return {'result':True}
            else:
                return {'result':False}
        return True

    @api.model
    def reprint_cupom_sat(self, chave, session_id):
        if not 'CFe' in chave:
            chave = 'CFe' + chave
        res = self.search([('chave_cfe','=',chave)])
        res_can = self.search([('chave_cfe_can','=',chave)])
        if res:
            reprint_search = self.env['ir.attachment'].search([('res_model','=','pos.order'),('res_id','=',res.id)])
            if reprint_search:
                reprint_xml = reprint_search.datas
                config_pos = self.env['pos.session'].browse(session_id).config_id
                conf_sat = self.env['hw.sat'].create_cfe_sat(config_pos.active_code_sat,
                                                    config_pos.library_path_sat,
                                                    config_pos.model_printer_sat,
                                                    config_pos.parameters_print_sat,
                                                    config_pos.sign_ac_sat,
                                                    config_pos.info_sat or '',
                                                    config_pos.print_connection,
                                                    res, 'reprint',chave,reprint_xml)
            else:
                # config_pos = self.env['pos.session'].browse(session_id).config_id
                # conf_sat = self.env['hw.sat'].create_cfe_sat(config_pos.active_code_sat,
                #                                     config_pos.library_path_sat,
                #                                     config_pos.model_printer_sat,
                #                                     config_pos.parameters_print_sat,
                #                                     config_pos.sign_ac_sat,
                #                                     config_pos.info_sat or '',
                #                                     config_pos.print_connection,
                #                                     res, 'reprint',chave,{})
                return False
        elif res_can:
            reprint_search = self.env['ir.attachment'].search([('res_model','=','pos.order'),('res_id','=',res_can.id)])
            if reprint_search:
                reprint_xml = reprint_search.datas
                config_pos = self.env['pos.session'].browse(session_id).config_id
                conf_sat = self.env['hw.sat'].create_cfe_sat(config_pos.active_code_sat,
                                                             config_pos.library_path_sat,
                                                             config_pos.model_printer_sat,
                                                             config_pos.parameters_print_sat,
                                                             config_pos.sign_ac_sat,
                                                             config_pos.info_sat or '',
                                                             config_pos.print_connection,
                                                             res_can, 'reprint',chave,reprint_xml)
            else:
                # config_pos = self.env['pos.session'].browse(session_id).config_id
                # conf_sat = self.env['hw.sat'].create_cfe_sat(config_pos.active_code_sat,
                #                                     config_pos.library_path_sat,
                #                                     config_pos.model_printer_sat,
                #                                     config_pos.parameters_print_sat,
                #                                     config_pos.sign_ac_sat,
                #                                     config_pos.info_sat or '',
                #                                     config_pos.print_connection,
                #                                     res, 'reprint',chave,{})
                return False

        else:
            return False
        return True


    @api.model
    def _order_fields(self, ui_order):
        fields = super(PosOrder, self)._order_fields(ui_order)
        if ui_order.get('cpf_nfse', 0):
            fields['cpf_nfse'] = ui_order.get('cpf_nfse', 0)
        if ui_order.get('authorizer_user_id', 0):
            fields['authorizer_user_id'] = ui_order.get('authorizer_user_id', 0)
        if ui_order.get('loyalty_points'):
            br_pos_session = self.env['pos.session'].browse(ui_order.get('pos_session_id'))
            point_per_currency = br_pos_session.config_id.loyalty_id.pp_currency
            won_point = round(ui_order.get('amount_total')) * point_per_currency
            fields['spending_point_loyalty'] = won_point - ui_order.get('loyalty_points')
            fields['points_won'] = ui_order.get('points_won')
            fields['points_spend'] = ui_order.get('points_spend')
        return fields

    def _process_order(self, pos_order):
        res = super(PosOrder, self)._process_order(pos_order)
        config_pos = res.session_id.config_id
        #conf_sat = self.env['hw.sat'].teste(config_pos.active_code_sat, '/usr/lib/libbemasat.so', 'bematech-mp4200th', '/dev/ttyS42:4200,8,1,N', 'dZXFmGq2V0W5C2muk2E6U1CI8mMzcThNKZoAVhknRPR5BvQtMFAo8cUQOJZA5DFil5fkb6XqhZNszms6/KvZTh+NJ1ZvdYnRMBxJ19WRheMNyMxtzZz72b1IbVNGPedU46lWuXDd83kb+O4GOU6l0DSTQE1Nv2jNSLCQQtYY2LMN7yqCL3IRYSaA2UuDmezk/szP02+nB3sccKECV05QCbVc42qxzsgD5xN8IH202m5np51Cocg+rDm1LdytrJpBbetIyUUHaeponC1bnDBMKn/AvvkF4mgD+3rseHqd7S0oOdDqFOnQ8J+ZvAG1WA+7Q1mdnXyWjgsbbJsOxXefAA==', pos_order)
        if not 'quotation' in pos_order and config_pos.active_sat:
            conf_sat = self.env['hw.sat'].create_cfe_sat(config_pos.active_code_sat,
                                                config_pos.library_path_sat,
                                                config_pos.model_printer_sat,
                                                config_pos.parameters_print_sat,
                                                config_pos.sign_ac_sat,
                                                config_pos.info_sat or '',
                                                config_pos.print_connection,
                                                res, 'send')
        return res

    @api.model
    def create_from_ui(self, orders):
        # Keep only new orders
        submitted_references = [o['data']['name'] for o in orders]
        pos_order = self.search([('pos_reference', 'in', submitted_references)])
        existing_orders = pos_order.read(['pos_reference'])
        existing_references = set([o['pos_reference'] for o in existing_orders])
        orders_to_save = [o for o in orders if o['data']['name'] not in existing_references]
        order_ids = []

        for tmp_order in orders_to_save:
            to_invoice = tmp_order['to_invoice']
            if 'quotation' in tmp_order:
                self.quotation = tmp_order['quotation']
            order = tmp_order['data']
            if to_invoice:
                self._match_payment_to_invoice(order)
            pos_order = self._process_order(order)
            order_ids.append(pos_order.id)
            try:
                pos_order.action_pos_order_paid()
            except psycopg2.OperationalError:
                # do not hide transactional errors, the order(s) won't be saved!
                raise
            except Exception as e:
                _logger.error('Could not fully process the POS Order: %s', tools.ustr(e))

            for statement in pos_order.statement_ids:

                if statement.journal_id.is_contingency:
                    order['card_banner'] = statement.journal_id.banner_name and statement.journal_id.banner_name or ''

            if to_invoice:
                pos_order.action_pos_order_invoice()
                pos_order.invoice_id.sudo().action_invoice_open()

            if tmp_order['data']['cpf_nfse'] != 0 and tmp_order['data']['partner_id']:
                partner = self.env['res.partner'].sudo().browse(tmp_order['data']['partner_id'])
                partner.write({'loyalty_points': partner['loyalty_points'] + tmp_order['data']['loyalty_points']})
        return order_ids

class NewPosLines(models.Model):
    _inherit = "pos.order.line"

    discount_total_by_line = fields.Float(string='Discount Total By Line')
    liquid = fields.Float(string='Discount Total By Line', related='order_id.total', store=True)
    discount_percent_by_line = fields.Float(string='Discount Total By Line')

class PosOrderReport(models.Model):
    _name = "pos.order.report"

    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    user_id = fields.Many2one('res.users', 'Salesman')
    product_id = fields.Many2one('product.product', 'Product')

    @api.multi
    def check_report(self):
        data_start_date = []
        data_end_date = []
        data_user_id = []
        data_product_id = []
        ids = []
        data = []

        brs_pos_order = self.env['pos.order'].search([('state', '!=', 'draft')])

        for order in brs_pos_order:
            for order_line in order.lines:
                data.append(order_line)

        if self.start_date:
            for br_pos_order_line in data:
                if br_pos_order_line.order_id.date_order[0:10] >= self.start_date:
                    data_start_date.append(br_pos_order_line)
            data =[]
            for reg in data_start_date:
                data.append(reg)

        if self.end_date:
            for br_pos_order_line in data:
                if br_pos_order_line.order_id.date_order[0:10] <= self.end_date:
                    data_end_date.append(br_pos_order_line)
            data =[]
            for reg in data_end_date:
                data.append(reg)

        if self.user_id:
            for br_pos_order_line in data:
                if br_pos_order_line.order_id.user_id.id == self.user_id.id:
                    data_user_id.append(br_pos_order_line)
            data =[]
            for reg in data_user_id:
                data.append(reg)

        if self.product_id:
            for br_pos_order_line in data:
                if br_pos_order_line.product_id.id == self.product_id.id:
                    data_product_id.append(br_pos_order_line)
            data =[]
            for reg in data_product_id:
                data.append(reg)

        for reg in data:
            ids.append(reg.id)

        return self.env['report'].get_action(ids, 'pos_ext.report_pos_discount')

class Reporteposorderreportranking(models.AbstractModel):
    _name = 'report.pos_ext.report_pos_discount_ranking'

    @api.multi
    def check_report(self):
        ids = []
        self.env.cr.execute("""
                select res_partner.name as name_user,
                    sum(DISTINCT pos_order.discount_total) + sum(pos_order_line.discount_fixed)
                    as total_valor,
                    sum((pos_order_line.valor_bruto - ((pos_order_line.valor_bruto * pos_order_line.discount / 100))) * pos_order.discount_percent / 100) +
                    sum(pos_order_line.valor_bruto * pos_order_line.discount / 100)
                    as total_percentual,
                    sum(DISTINCT pos_order.discount_total) + sum(pos_order_line.discount_fixed) +
                    sum(pos_order_line.valor_bruto * pos_order_line.discount / 100) +
                    sum((pos_order_line.valor_bruto - ((pos_order_line.valor_bruto * pos_order_line.discount / 100))) * pos_order.discount_percent / 100)
                    as total,
                    sum(pos_order_line.valor_bruto) - sum(DISTINCT pos_order.discount_total) + sum(pos_order_line.discount_fixed) - sum((pos_order_line.valor_bruto - ((pos_order_line.valor_bruto * pos_order_line.discount / 100))) * pos_order.discount_percent / 100) +
                    sum(pos_order_line.valor_bruto * pos_order_line.discount / 100)
                    as total_vendas,
                    sum(pos_order_line.valor_bruto) - ((sum(pos_order_line.valor_bruto) - ((sum(pos_order_line.valor_bruto) * sum(pos_order_line.discount) / 100))) * sum(DISTINCT pos_order.discount_percent / 100))
                    as total_recebido
                    from pos_order cross join pos_order_line  cross join res_partner cross join res_users
                    where pos_order.id = pos_order_line.order_id and pos_order_line.valor_bruto >= 0 and
                pos_order.user_id = res_users.id and res_users.partner_id = res_partner.id and pos_order.date_order >= %s and pos_order.date_order <= %s group by res_partner.name order by total DESC
            """, (self.start_date,self.end_date))
        dict_ranking = self.env.cr.dictfetchall()

        return dict_ranking
    @api.model
    def render_html(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_ids', []))

        docargs = {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'data': data['form'],
            'start_date': data['start_d'],
            'end_date': data['stop_d'],
            'logo': data['logo'],
            'docs': docs,
            'lines': {},
        }
        return self.env['report'].render('pos_ext.report_pos_discount_ranking', docargs)

class PosOrderReportRanking(models.Model):
    _name = "pos.order.report.ranking"

    start_date = fields.Date('Start Date', required=True)
    end_date = fields.Date('End Date', required=True)


    @api.multi
    def check_report(self):
        ids = []
        self.env.cr.execute("""
                select res_partner.name as name_user,
                    sum(DISTINCT pos_order.discount_total) + sum(pos_order_line.discount_fixed)
                    as total_valor,
                    sum((pos_order_line.valor_bruto - ((pos_order_line.valor_bruto * pos_order_line.discount / 100))) * pos_order.discount_percent / 100) +
                    sum(pos_order_line.valor_bruto * pos_order_line.discount / 100)
                    as total_percentual,
                    sum(DISTINCT pos_order.discount_total) + sum(pos_order_line.discount_fixed) +
                    sum(pos_order_line.valor_bruto * pos_order_line.discount / 100) +
                    sum((pos_order_line.valor_bruto - ((pos_order_line.valor_bruto * pos_order_line.discount / 100))) * pos_order.discount_percent / 100)
                    as total,
                    sum(pos_order_line.valor_bruto) - sum(DISTINCT pos_order.discount_total) + sum(pos_order_line.discount_fixed) - sum((pos_order_line.valor_bruto - ((pos_order_line.valor_bruto * pos_order_line.discount / 100))) * pos_order.discount_percent / 100) +
                    sum(pos_order_line.valor_bruto * pos_order_line.discount / 100)
                    as total_vendas,
                    sum(pos_order_line.valor_bruto) - ((sum(pos_order_line.valor_bruto) - ((sum(pos_order_line.valor_bruto) * sum(pos_order_line.discount) / 100))) * sum(DISTINCT pos_order.discount_percent / 100))
                    as total_recebido
                    from pos_order cross join pos_order_line  cross join res_partner cross join res_users
                    where pos_order.id = pos_order_line.order_id and pos_order_line.valor_bruto >= 0 and
                pos_order.user_id = res_users.id and res_users.partner_id = res_partner.id and pos_order.date_order >= %s and pos_order.date_order <= %s group by res_partner.name order by total DESC
            """, (self.start_date + ' 00:00:00',self.end_date + ' 23:59:00'))
        dict_ranking = self.env.cr.dictfetchall()

        return dict_ranking


    def print_report(self):
        active_ids = self.env.context.get('active_ids', [])
        data = {
            'ids': active_ids,
            'model': self.env.context.get('active_model', 'ir.ui.menu'),
            'form': self.check_report(),
            'start_d': self.start_date,
            'stop_d': self.end_date,
            'logo': self.env['res.users'].browse(self._uid).company_id.logo_web
        }
        return self.env['report'].get_action([], 'pos_ext.report_pos_discount_ranking', data=data)



class PosOrderLog(models.Model):
    _name = 'pos.order.log'

    pos_order_id = fields.Many2one('pos.order','Pos Order')
    log = fields.Char('Log')

class PosConfig(models.Model):
    _inherit = "pos.config"

    default_account_id = fields.Many2one('account.account', string=_('Customer Transitory Account'), required=True)
    # discount_account_id = fields.Many2one('account.account', string=_('Discount Account'), required=True)
    is_password_quantity = fields.Boolean(string='Quantity')
    password_quantity = fields.Char(string='Password')
    is_password_price = fields.Boolean(string='Price')
    password_price = fields.Char(string='Password')
    is_password_discount = fields.Boolean(string='Discount')
    password_discount = fields.Char(string='Password Discount')
    is_password_backspace = fields.Boolean(string='Backspace')
    password_backspace = fields.Char(string='Password')
    is_password_wallet = fields.Boolean(string='Payment Wallet')
    password_wallet = fields.Char(string='Password Wallet')

    #Configuracao para SAT
    active_code_sat = fields.Char(string='Active Code Sat', help='EX: 123456789')
    library_path_sat = fields.Char(string='Path Sat', help='EX: /usr/lib/libbemasat.so')
    model_printer_sat = fields.Char(string='Model Printer Sat', help='EX: Models=(epson-tm-t20, bematech-mp4200th, daruma-dr700, elgin-i9)')
    parameters_print_sat = fields.Char(string='Parameter Printer Sat', help='EX: Serial:(/dev/ttyS42:4200,8,1,N) ou Rede(192.168.0.165:9100)')
    sign_ac_sat = fields.Text(string='Path Sat', help='EX: dZXFmGq2V0W5C2muk2E6U1CI8mMzcThNKZoAVhknRPR5BvQtMFAo8cUQOJZA5DFil5fkb6XqhZNszms6/KvZTh+NJ1ZvdYnRMBxJ19WRheMNyMxtzZz72b1IbVNGPedU46lWuXDd83kb+O4GOU6l0DSTQE1Nv2jNSLCQQtYY2LMN7yqCL3IRYSaA2UuDmezk/szP02+nB3sccKECV05QCbVc42qxzsgD5xN8IH202m5np51Cocg+rDm1LdytrJpBbetIyUUHaeponC1bnDBMKn/AvvkF4mgD+3rseHqd7S0oOdDqFOnQ8J+ZvAG1WA+7Q1mdnXyWjgsbbJsOxXefAA==')
    info_sat = fields.Text(string='Info Sat', default='Tributos Aprox R$ Fonte IBPT Fed: @federal Est: @estadual Mun: @municial - Valores serão colocado no lugar as variveis (@federal,@estadual,@municipal)', help='EX: Tributos Aprox R$ Fonte IBPT Fed: @federal Est: @estadual Mun: @municial - Valores serão colocado no lugar as variveis (@federal,@estadual,@municipal)')
    active_sat = fields.Boolean(string='Active SAT')
    print_connection = fields.Selection([('network','Network'),('serial','Serial')],string='Network Connection')

    @api.multi
    def open_session_cb(self):
        assert len(self.ids) == 1, "you can open only one session at a time"
        user = self.env['res.users'].sudo().browse(self._uid)
        if not self.current_session_id:
            self.current_session_id = self.env['pos.session'].create({
                'user_id': self.env.uid,
                'config_id': self.id
            })
            if self.current_session_id.state == 'opened':
                return self.open_ui()
        if self.current_session_id.state == 'opened' and not user.pos_manager and not self.current_session_id.declared_value:
            validate_id = self.env['payment.validate.pos'].create({'session_id':self.current_session_id.id})
            for i in self.journal_ids:
                self.env['payment.validate.line.pos'].create(
                    {
                        'journal_id': i.id,
                        'payment_validate':validate_id.id
                    }
                )
            return {
                'name': _('Session'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'payment.validate.pos',
                'res_id': validate_id.id,
                'view_id': False,
                'type': 'ir.actions.act_window',
                'target':'new'
            }

        #     return self._open_session(self.current_session_id.id)
        return self._open_session(self.current_session_id.id)

    @api.multi
    def open_existing_session_cb_close(self):
        assert len(self.ids) == 1, "you can open only one session at a time"
        if self.current_session_id.cash_control:
            self.current_session_id.action_pos_session_closing_control()
        user = self.env['res.users'].sudo().browse(self._uid)
        if self.current_session_id.state in ['opened','closing_control'] and not user.pos_manager and not self.current_session_id.declared_value:
            validate_id = self.env['payment.validate.pos'].create({'session_id':self.current_session_id.id})
            for i in self.journal_ids:
                self.env['payment.validate.line.pos'].create(
                    {
                        'journal_id': i.id,
                        'payment_validate':validate_id.id
                    }
                )
            return {
                'name': _('Session'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'payment.validate.pos',
                'res_id': validate_id.id,
                'view_id': False,
                'type': 'ir.actions.act_window',
                'target':'new'
            }

        return self.open_session_cb()

    @api.multi
    def open_existing_session_cb(self):
        assert len(self.ids) == 1, "you can open only one session at a time"
        user = self.env['res.users'].sudo().browse(self._uid)
        if self.current_session_id.state in ['opened','closing_control'] and not user.pos_manager and not self.current_session_id.declared_value:
            validate_id = self.env['payment.validate.pos'].create({'session_id':self.current_session_id.id})
            for i in self.journal_ids:
                self.env['payment.validate.line.pos'].create(
                    {
                        'journal_id': i.id,
                        'payment_validate':validate_id.id
                    }
                )
            return {
                'name': _('Session'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'payment.validate.pos',
                'res_id': validate_id.id,
                'view_id': False,
                'type': 'ir.actions.act_window',
                'target':'new'
            }

        return self._open_session(self.current_session_id.id)


class PaymentValidatePos(models.TransientModel):
    _name = "payment.validate.pos"

    session_id = fields.Many2one('pos.session', string='Config POS')
    line_ids = fields.One2many('payment.validate.line.pos', 'payment_validate', string='Validate Lines')

    def validate_value(self):
        user = self.env['res.users'].sudo().browse(self._uid)
        for l in self.line_ids:
            for i in self.session_id.statement_ids:
                if l.journal_id.id == i.journal_id.id:
                    value_difference = float('%.2f' % i.balance_end) - float('%.2f' % l.amount_total)
                    i.write({'amount_declared':l.amount_total,'value_difference_box':value_difference})
        self.session_id.write({'declared_value':True})
                    # if l.amount_total == i.balance_end:
                    #     continue
                    # else:
                    #     raise UserError(_(u'Diferença no valor total de (%s)' % (i.journal_id.name)))
        return self.env['pos.config']._open_session(self.session_id.id)

class PaymentValidateLinePos(models.TransientModel):
    _name = "payment.validate.line.pos"

    journal_id = fields.Many2one('account.journal',string='Journal')
    amount_total = fields.Float(string='Amount Total')
    payment_validate = fields.Many2one('payment.validate.pos',string='Payment Validate')


class PosDetails(models.TransientModel):
    _inherit = 'pos.details.wizard'

    @api.multi
    def generate_report(self):
        data = {'date_start': self.start_date, 'date_stop': self.end_date}
        data.update(self.env['report.point_of_sale.report_saledetails'].get_sale_details_ext(
            self.start_date, self.end_date, self.pos_config_ids))
        return self.env['report'].get_action(
            [], 'point_of_sale.report_saledetails', data=data)


class ReportSaleDetails(models.AbstractModel):

    _inherit = 'report.point_of_sale.report_saledetails'

    @api.model
    def get_sale_details_ext(self, date_start=False, date_stop=False, configs=False):
        """ Serialise the orders of the day information

        params: date_start, date_stop string representing the datetime of order
        """
        if not configs:
            configs = self.env['pos.config'].search([])

        today = fields.Datetime.from_string(fields.Date.context_today(self))
        if date_start:
            date_start = fields.Datetime.from_string(date_start)
        else:
            # start by default today 00:00:00
            date_start = today

        if date_stop:
            # set time to 23:59:59
            date_stop = fields.Datetime.from_string(date_stop)
        else:
            # stop by default today 23:59:59
            date_stop = today + timedelta(days=1, seconds=-1)

        # avoid a date_stop smaller than date_start
        date_stop = max(date_stop, date_start)

        date_start = fields.Datetime.to_string(date_start)
        date_stop = fields.Datetime.to_string(date_stop)

        orders = self.env['pos.order'].search([
            ('date_order', '>=', date_start),
            ('date_order', '<=', date_stop),
            ('state', 'in', ['paid','invoiced','done']),
            ('config_id', 'in', configs.ids)])

        user_currency = self.env.user.company_id.currency_id

        total = 0.0
        products_sold = {}
        taxes = {}
        for order in orders:
            if user_currency != order.pricelist_id.currency_id:
                total += order.pricelist_id.currency_id.compute(order.amount_total, user_currency)
            else:
                total += order.amount_total
            currency = order.session_id.currency_id

            for line in order.lines:
                key = (line.product_id, line.price_unit, line.discount)
                products_sold.setdefault(key, 0.0)
                products_sold[key] += line.qty
                account_tax = self.env['account.tax']
                ids = []
                for i in line.tax_ids_after_fiscal_position:
                    if i.id:
                        ids.append(i.id)
                new_taxs = account_tax.browse(ids)
                line.tax_ids_after_fiscal_position = new_taxs
                if line.tax_ids_after_fiscal_position:
                    line_taxes = line.tax_ids_after_fiscal_position.compute_all(line.price_unit * (1-(line.discount or 0.0)/100.0), currency, line.qty, product=line.product_id, partner=line.order_id.partner_id or False)
                    for tax in line_taxes['taxes']:
                        taxes.setdefault(tax['id'], {'name': tax['name'], 'total':0.0})
                        taxes[tax['id']]['total'] += tax['amount']

        st_line_ids = self.env["account.bank.statement.line"].search([('pos_statement_id', 'in', orders.ids)]).ids
        if st_line_ids:
            self.env.cr.execute("""
                SELECT aj.name, sum(amount) total
                FROM account_bank_statement_line AS absl,
                     account_bank_statement AS abs,
                     account_journal AS aj
                WHERE absl.statement_id = abs.id
                    AND abs.journal_id = aj.id
                    AND absl.id IN %s
                GROUP BY aj.name
            """, (tuple(st_line_ids),))
            payments = self.env.cr.dictfetchall()
        else:
            payments = []

        return {
            'total_paid': user_currency.round(total),
            'payments': payments,
            'company_name': self.env.user.company_id.name,
            'taxes': taxes.values(),
            'products': sorted([{
                'product_id': product.id,
                'product_name': product.name,
                'code': product.default_code,
                'quantity': qty,
                'price_unit': price_unit,
                'discount': discount,
                'uom': product.uom_id.name
            } for (product, price_unit, discount), qty in products_sold.items()], key=lambda l: l['product_name'])
        }

    @api.multi
    def render_html(self, docids, data=None):
        company = request.env.user.company_id
        date_start = self.env.context.get('date_start', False)
        date_stop = self.env.context.get('date_stop', False)
        data = dict(data or {}, date_start=date_start, date_stop=date_stop)
        _logger.info('%s', data)
        #data.update(self.get_sale_details(date_start, date_stop, company))
        return self.env['report'].render('point_of_sale.report_saledetails', data)

class PosOrderReportAmount(models.Model):
    _inherit = "report.pos.order"

    liquid_total = fields.Float(string='Liquid Total')



    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'report_pos_order')
        self._cr.execute("""
            CREATE OR REPLACE VIEW report_pos_order AS (
                SELECT
                    MIN(l.id) AS id,
                    COUNT(*) AS nbr_lines,
                    s.date_order AS date,
                    SUM(l.qty * u.factor) AS product_qty,
                    SUM(l.liquid) AS price_sub_total,
                    SUM((l.qty * l.price_unit)  ) AS price_total,
                    SUM((l.qty * l.price_unit) - l.liquid) AS total_discount,
                    SUM(l.liquid) AS liquid_total, 
                    SUM(l.qty*l.price_unit) AS average_price,
                    SUM(cast(to_char(date_trunc('day',s.date_order) - date_trunc('day',s.create_date),'DD') AS INT)) AS delay_validation,
                    s.id as order_id,
                    s.discount_total AS discount_total,
                    s.partner_id AS partner_id,
                    s.state AS state,
                    s.user_id AS user_id,
                    s.location_id AS location_id,
                    s.company_id AS company_id,
                    s.sale_journal AS journal_id,
                    l.product_id AS product_id,
                    pt.categ_id AS product_categ_id,
                    p.product_tmpl_id,
                    ps.config_id,
                    pt.pos_categ_id,
                    pc.stock_location_id,
                    s.pricelist_id,
                    s.session_id,
                    s.invoice_id IS NOT NULL AS invoiced
                    FROM pos_order_line AS l
                    LEFT JOIN pos_order s    ON (s.id=l.order_id)
                    LEFT JOIN product_product p ON (l.product_id=p.id)
                    LEFT JOIN product_template pt ON (p.product_tmpl_id=pt.id)
                    LEFT JOIN product_uom u ON (u.id=pt.uom_id)
                    LEFT JOIN pos_session ps ON (s.session_id=ps.id)
                    LEFT JOIN pos_config pc ON (ps.config_id=pc.id)
                GROUP BY
                    s.id, s.date_order, s.partner_id,s.state, pt.categ_id,
                    s.user_id, s.location_id, s.company_id, s.sale_journal,
                    s.pricelist_id, s.invoice_id, s.create_date, s.session_id,
                    l.product_id,
                    pt.categ_id, pt.pos_categ_id,
                    p.product_tmpl_id,
                    ps.config_id,
                    s.amountx_totalx,
                    pc.stock_location_id
                HAVING
                    SUM(l.qty * u.factor) != 0
            )
        """)

