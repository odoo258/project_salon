# coding=utf-8
# Author: Christian Douglas <christian.douglas.alcantara@gmail.com>
from odoo import models, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def action_invoice_paid(self):
        super(AccountInvoice, self).action_invoice_paid()
        sale_order = self.env['sale.order']
        for invoice in self:
            invoice_line_id = invoice.invoice_line_ids[0].id
            sql = """SELECT order_id 
                     FROM   sale_order_line 
                            INNER JOIN sale_order_line_invoice_rel 
                                    ON sale_order_line_invoice_rel.order_line_id = sale_order_line.id 
                     WHERE  sale_order_line_invoice_rel.invoice_line_id = {};"""
            self.env.cr.execute(sql.format(invoice_line_id))
            query_results = self.env.cr.dictfetchall()
            if query_results:
                sale_order_obj = sale_order.browse(query_results[0].get('order_id'))
                paid = True
                admission_id = sale_order_obj.admission_id
                medical_map = self.env['medical.map']
                for ol in sale_order_obj.order_line:
                    omap = medical_map.search([('sale_order_line_id', '=', ol.id)], limit=1)
                    if omap:
                        if omap.name == 'hospitalization':
                            omap.state = 'hospitalized'
                        else:
                            omap.state = 'closed'

                for so in sale_order_obj.admission_id.sale_order_ids:
                    for inv in so.invoice_ids:
                        if inv.state not in ['paid', 'cancel']:
                            paid = False
                            break
                domain = [
                    ('admission_id', '=', admission_id.id),
                    ('state', 'in', ['draft', 'open', 'approved'])
                ]
                if paid and not medical_map.search(domain):
                    admission_id.action_done()
