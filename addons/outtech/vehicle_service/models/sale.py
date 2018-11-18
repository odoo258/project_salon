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
from odoo.exceptions import UserError
from dateutil import relativedelta
from datetime import date

class SaleOrder(models.Model):
    _inherit = "sale.order"

    quick_sale_id = fields.Many2one('quick.sale', string="Quick Sale")

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        if 'uid' in self._context:
            user = self.env['res.users'].browse(self._context['uid'])
            resale_manager = self.env['crm.team'].search([('user_id','=',user.id)])
            if not user.is_master:
                args.append(['user_id','=',user.id])
            if resale_manager:
                user_team = resale_manager.member_ids.ids
                user_team.append(user.id)
                args.append(['user_id','in',user_team])
        return super(SaleOrder, self).search(args, offset=offset, limit=limit, order=order, count=count)


    @api.multi
    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        if self.quick_sale_id:
            date_new = date.today() + relativedelta.relativedelta(days=30)
            value = {
                'partner_id': self.partner_id.id,
                'pricelist_id': self.pricelist_id.id,
                'template_id': 1,
                'company_id': self.company_id.id,
            }

            sale_subscription = self.env['sale.subscription'].create(value)
            if self.quick_sale_id:
                value_line = {
                    'name': self.quick_sale_id.plan_id_product.name,
                    'product_id': self.quick_sale_id.plan_id_product.id,
                    'uom_id': self.quick_sale_id.plan_id_product.uom_id.id,
                    'price_subtotal': self.quick_sale_id.plan_id_product.lst_price,
                    'price_unit': self.quick_sale_id.plan_id_product.lst_price,
                    'analytic_account_id': sale_subscription.id,
                    'sold_quantity': 1,
                    'quantity': 1,
                }
                self.env['sale.subscription.line'].create(value_line)

            type_installation = self.env['installation.schedule.type'].sudo().search([('type','=','inst')])

            vals = {
                'name': self.env['ir.sequence'].next_by_code('installation.schedule') or 'New',
                'partner_id': self.partner_id.id,
                'sale_order_id': self.id,
                'contract_id': sale_subscription.id,
                'type_id': type_installation.id
            }

            self.env['installation.schedule'].create(vals)

            # Create invoice

            # self.action_invoice_create()

        return res

    @api.multi
    def _prepare_invoice(self):
        """
        Prepare the dict of values to create the new invoice for a sales order. This method may be
        overridden to implement custom invoice generation (making sure to call super() to establish
        a clean extension chain).
        """
        self.ensure_one()
        if self.quick_sale_id:
            auto = False
        else:
            auto = True
        journal_id = self.env['account.invoice'].default_get(['journal_id'])['journal_id']
        if not journal_id:
            raise UserError(_('Please define an accounting sale journal for this company.'))
        invoice_vals = {
            'name': self.client_order_ref or '',
            'origin': self.name,
            'type': 'out_invoice',
            'account_id': self.partner_invoice_id.property_account_receivable_id.id,
            'partner_id': self.partner_invoice_id.id,
            'partner_shipping_id': self.partner_shipping_id.id,
            'journal_id': journal_id,
            'currency_id': self.pricelist_id.currency_id.id,
            'comment': self.note,
            'payment_term_id': self.payment_term_id.id,
            'fiscal_position_id': self.fiscal_position_id.id or self.partner_invoice_id.property_account_position_id.id,
            'company_id': self.company_id.id,
            'user_id': self.user_id and self.user_id.id,
            'team_id': self.team_id.id,
            'automatic_process': auto,
            'sale_id': self.id
        }
        return invoice_vals

    # @api.model
    # def create(self, vals):
    #
    #     if not 'quick_sale_id' in vals:
    #
    #         template_id = self.env['mail.template'].search([('id', '=', self.env.ref('vehicle_service.email_template_sale_order_mail').id)])
    #
    #         if not template_id:
    #             raise UserError(_('There is no email template for sale confirmation'))
    #
    #         res = super(SaleOrder, self).create(vals)
    #
    #         mail_values = template_id.generate_email(res.id)
    #
    #         br_ir = self.env['ir.config_parameter'].search([('key', '=', 'web.base.url')])
    #
    #         link = br_ir.value + '/api/email/return/sale?' + 'sale_order=%s' % (str(res.id))
    #
    #         body_html = mail_values['body_html'].replace('@link', link)
    #
    #         vals_email = {
    #             'subject': mail_values['subject'],
    #             'email_from': mail_values['email_from'],
    #             'email_to': mail_values['email_to'],
    #             'body_html': body_html,
    #             'auto_delete': False,
    #             'state': 'outgoing',
    #             'model': mail_values['model'],
    #             'res_id': mail_values['res_id'],
    #         }
    #
    #         self.env['mail.mail'].create(vals_email)
    #
    #     else:
    #         res = super(SaleOrder, self).create(vals)
    #
    #     return res