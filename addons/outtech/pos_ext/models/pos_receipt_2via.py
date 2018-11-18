# -*- coding: utf-8 -*-

import time
from odoo import models, api
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
            'order': self._get_order,
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

    def _get_order(self, order_id):
        sql = 'select * from pos_order where order_id = %s '
        self.cr.execute(sql, (order_id,))
        res = self.cr.fetchall()

        return res

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
    _name = 'report.pos_ext.report_receipt_2via'
    _inherit = 'report.abstract_report'
    _template = 'pos_ext.report_receipt_2via'
    _wrapped_report_class = order


    @api.model
    def render_html(self, docids, data=None):
        context = dict(self.env.context or {})

        # If the key 'landscape' is present in data['form'], passing it into the context
        if data and data.get('form', {}).get('landscape'):
            context['landscape'] = True

        if context and context.get('active_ids'):
            # Browse the selected objects via their reference in context
            model = context.get('active_model') or context.get('model')
            objects_model = self.env[model]
            objects = objects_model.with_context(context).browse(context['active_ids'])
        else:
            # If no context is set (for instance, during test execution), build one
            model = self.env['report']._get_report_from_name(self._template).model
            objects_model = self.env[model]
            objects = objects_model.with_context(context).browse(docids)
            context['active_model'] = model
            context['active_ids'] = docids

        # Generate the old style report
        wrapped_report = self.with_context(context)._wrapped_report_class(self.env.cr, self.env.uid, '', context=context)
        wrapped_report.set_context(objects, data, context['active_ids'])

        # Rendering self._template with the wrapped report instance localcontext as
        # rendering environment
        docargs = dict(wrapped_report.localcontext)
        if not docargs.get('lang'):
            docargs.pop('lang', False)
        docargs['docs'] = docargs.get('objects')

        # Used in template translation (see translate_doc method from report model)
        docargs['doc_ids'] = context['active_ids']
        docargs['doc_model'] = model
        docargs['order'] = docargs['objects']

        return self.env['report'].with_context(context).render(self._template, docargs)