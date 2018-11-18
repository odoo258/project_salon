# -*- coding: utf-8 -*-

import time
from odoo import models
from odoo.report import report_sxw


def titlize(journal_name):
    words = journal_name.split()
    while words.pop() != 'journal':
        continue
    return ' '.join(words)


class order(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(order, self).__init__(cr, uid, name, context=context)

        # user = self.env['res.users'].browse(self._uid)
        # partner = user.company_id.partner_id

        self.localcontext.update({
            'time': time,
            'disc': self.discount,
            'net': self.netamount,
            'get_journal_amt': self._get_journal_amt,
            'address': False,#partner or False,
            'titlize': titlize
        })

    def netamount(self, order_line_id):
        sql = 'select (qty*price_unit) as net_price from pos_order_line where id = %s'
        self.cr.execute(sql, (order_line_id,))
        res = self.cr.fetchone()
        return res[0]

    def discount(self, order_id):
        sql = 'select discount, discount_fixed, price_unit, qty from pos_order_line where order_id = %s '
        self.cr.execute(sql, (order_id,))
        res = self.cr.fetchall()
        dsum = 0
        for line in res:
            if line[1] != 0:
                dsum = dsum + (line[1])
            else:
                dsum = dsum + (line[3] * (line[0] * line[2] / 100))
        return dsum

    def _get_journal_amt(self, order_id):
        data={}
        sql = """ select aj.name,absl.amount as amt from account_bank_statement as abs
                        LEFT JOIN account_bank_statement_line as absl ON abs.id = absl.statement_id
                        LEFT JOIN account_journal as aj ON aj.id = abs.journal_id
                        WHERE absl.pos_statement_id =%d"""%(order_id)
        self.cr.execute(sql)
        data = self.cr.dictfetchall()
        return data


class report_order_receipt(models.AbstractModel):
    _name = 'report.discounts_in_pos.report_receipt'
    _inherit = 'report.abstract_report'
    _template = 'discounts_in_pos.report_receipt'
    _wrapped_report_class = order
