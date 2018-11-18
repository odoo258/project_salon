# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp import api, fields, models


class CustomerVendorStatement(models.AbstractModel):
    """Model of Customer Activity Statement"""

    _name = 'report.customer_statement.statement'

    def _format_date_to_partner_lang(self, str_date, partner_id):
        lang_code = self.env['res.partner'].browse(partner_id).lang
        lang_id = self.env['res.lang']._lang_get(lang_code)
        lang = self.env['res.lang'].browse(lang_id)
        date = datetime.strptime(str_date, DEFAULT_SERVER_DATE_FORMAT).date()
        return date.strftime(lang_id.date_format)

    def _initial_balance_sql_q1(self, partners, date_start):
        return """
            SELECT l.partner_id, l.currency_id, l.company_id,
            CASE WHEN l.currency_id is not null AND l.amount_currency > 0.0
                THEN sum(l.amount_currency)
                ELSE sum(l.debit)
            END as debit,
            CASE WHEN l.currency_id is not null AND l.amount_currency < 0.0
                THEN sum(l.amount_currency * (-1))
                ELSE sum(l.credit)
            END as credit
            FROM account_move_line l
            JOIN account_account_type at ON (at.id = l.user_type_id)
            JOIN account_move m ON (l.move_id = m.id)
            WHERE l.partner_id IN (%s) AND at.type = 'receivable'
                                AND l.date <= '%s' AND not l.blocked
            GROUP BY l.partner_id, l.currency_id, l.amount_currency,
                                l.company_id
        """ % (partners, date_start)
    def _initial_balance_sql_q1_payable(self, partners, date_start):
        return """
            SELECT l.partner_id, l.currency_id, l.company_id,
            CASE WHEN l.currency_id is not null AND l.amount_currency > 0.0
                THEN sum(l.amount_currency)
                ELSE sum(l.debit)
            END as debit,
            CASE WHEN l.currency_id is not null AND l.amount_currency < 0.0
                THEN sum(l.amount_currency * (-1))
                ELSE sum(l.credit)
            END as credit
            FROM account_move_line l
            JOIN account_account_type at ON (at.id = l.user_type_id)
            JOIN account_move m ON (l.move_id = m.id)
            WHERE l.partner_id IN (%s) AND at.type = 'payable'
                                AND l.date <= '%s' AND not l.blocked
            GROUP BY l.partner_id, l.currency_id, l.amount_currency,
                                l.company_id
        """ % (partners, date_start)
    def _initial_balance_sql_q1_receivable_and_payable(self, partners, date_start):
        return """
            SELECT l.partner_id, l.currency_id, l.company_id,
            CASE WHEN l.currency_id is not null AND l.amount_currency > 0.0
                THEN sum(l.amount_currency)
                ELSE sum(l.debit)
            END as debit,
            CASE WHEN l.currency_id is not null AND l.amount_currency < 0.0
                THEN sum(l.amount_currency * (-1))
                ELSE sum(l.credit)
            END as credit
            FROM account_move_line l
            JOIN account_account_type at ON (at.id = l.user_type_id)
            JOIN account_move m ON (l.move_id = m.id)
            WHERE l.partner_id IN (%s) AND (at.type = 'payable' OR at.type = 'receivable')
                                AND l.date <= '%s' AND not l.blocked
            GROUP BY l.partner_id, l.currency_id, l.amount_currency,
                                l.company_id
        """ % (partners, date_start)


    def _initial_balance_sql_q2(self, company_id):
        return """
            SELECT Q1.partner_id, debit-credit AS balance,
            COALESCE(Q1.currency_id, c.currency_id) AS currency_id
            FROM Q1
            JOIN res_company c ON (c.id = Q1.company_id)
            WHERE c.id = %s
        """ % company_id
    def _initial_balance_sql_q2_payable(self, company_id):
        return """
            SELECT Q1.partner_id, debit-credit AS balance,
            COALESCE(Q1.currency_id, c.currency_id) AS currency_id
            FROM Q1
            JOIN res_company c ON (c.id = Q1.company_id)
            WHERE c.id = %s
        """ % company_id
    def _initial_balance_sql_q2_receivable_and_payable(self, company_id):
        return """
            SELECT Q1.partner_id, debit-credit AS balance,
            COALESCE(Q1.currency_id, c.currency_id) AS currency_id
            FROM Q1
            JOIN res_company c ON (c.id = Q1.company_id)
            WHERE c.id = %s
        """ % company_id


    def _get_account_initial_balance(self, company_id, partner_ids,
                                     date_start):
        res = dict(map(lambda x: (x, []), partner_ids))
        partners = ', '.join([str(i) for i in partner_ids])
        date_start = datetime.strptime(
            date_start, DEFAULT_SERVER_DATE_FORMAT).date()
        self.env.cr.execute("""WITH Q1 AS (%s), Q2 AS (%s)
        SELECT partner_id, currency_id, balance
        FROM Q2""" % (self._initial_balance_sql_q1(partners, date_start),
                      self._initial_balance_sql_q2(company_id)))
        for row in self.env.cr.dictfetchall():
            res[row.pop('partner_id')].append(row)
        return res
    def _get_account_initial_balance_payable(self, company_id, partner_ids,
                                     date_start):
        res = dict(map(lambda x: (x, []), partner_ids))
        partners = ', '.join([str(i) for i in partner_ids])
        date_start = datetime.strptime(
            date_start, DEFAULT_SERVER_DATE_FORMAT).date()
        self.env.cr.execute("""WITH Q1 AS (%s), Q2 AS (%s)
        SELECT partner_id, currency_id, balance
        FROM Q2""" % (self._initial_balance_sql_q1_payable(partners, date_start),
                      self._initial_balance_sql_q2_payable(company_id)))
        for row in self.env.cr.dictfetchall():
            res[row.pop('partner_id')].append(row)
        return res
    def _get_account_initial_balance_receivable_and_payable(self, company_id, partner_ids,
                                     date_start):
        res = dict(map(lambda x: (x, []), partner_ids))
        partners = ', '.join([str(i) for i in partner_ids])
        date_start = datetime.strptime(
            date_start, DEFAULT_SERVER_DATE_FORMAT).date()
        self.env.cr.execute("""WITH Q1 AS (%s), Q2 AS (%s)
        SELECT partner_id, currency_id, balance
        FROM Q2""" % (self._initial_balance_sql_q1_receivable_and_payable(partners, date_start),
                      self._initial_balance_sql_q2_receivable_and_payable(company_id)))
        for row in self.env.cr.dictfetchall():
            res[row.pop('partner_id')].append(row)
        return res

    def _display_lines_sql_q1(self, partners, date_start, date_end):
        return """
            SELECT m.name AS move_id, l.partner_id, l.date, l.name,
                                l.ref, l.blocked, l.currency_id, l.company_id,
            CASE WHEN (l.currency_id is not null AND l.amount_currency > 0.0)
                THEN sum(l.amount_currency)
                ELSE sum(l.debit)
            END as debit,
            CASE WHEN (l.currency_id is not null AND l.amount_currency < 0.0)
                THEN sum(l.amount_currency * (-1))
                ELSE sum(l.credit)
            END as credit,
            CASE WHEN l.date_maturity is null
                THEN l.date
                ELSE l.date_maturity
            END as date_maturity
            FROM account_move_line l
            JOIN account_account_type at ON (at.id = l.user_type_id)
            JOIN account_move m ON (l.move_id = m.id)
            WHERE l.partner_id IN (%s) AND at.type = 'receivable'
                                AND '%s' < l.date AND l.date <= '%s'
            GROUP BY l.partner_id, m.name, l.date, l.date_maturity, l.name,
                                l.ref, l.blocked, l.currency_id,
                                l.amount_currency, l.company_id
        """ % (partners, date_start, date_end)
    def _display_lines_sql_q1_payable(self, partners, date_start, date_end):
        return """
            SELECT m.name AS move_id, l.partner_id, l.date, l.name,
                                l.ref, l.blocked, l.currency_id, l.company_id,
            CASE WHEN (l.currency_id is not null AND l.amount_currency > 0.0)
                THEN sum(l.amount_currency)
                ELSE sum(l.debit)
            END as debit,
            CASE WHEN (l.currency_id is not null AND l.amount_currency < 0.0)
                THEN sum(l.amount_currency * (-1))
                ELSE sum(l.credit)
            END as credit,
            CASE WHEN l.date_maturity is null
                THEN l.date
                ELSE l.date_maturity
            END as date_maturity
            FROM account_move_line l
            JOIN account_account_type at ON (at.id = l.user_type_id)
            JOIN account_move m ON (l.move_id = m.id)
            WHERE l.partner_id IN (%s) AND at.type = 'payable'
                                AND '%s' < l.date AND l.date <= '%s'
            GROUP BY l.partner_id, m.name, l.date, l.date_maturity, l.name,
                                l.ref, l.blocked, l.currency_id,
                                l.amount_currency, l.company_id
        """ % (partners, date_start, date_end)
    def _display_lines_sql_q1_receivable_and_payable(self, partners, date_start, date_end):
        return """
            SELECT m.name AS move_id, l.partner_id, l.date, l.name,
                                l.ref, l.blocked, l.currency_id, l.company_id,
            CASE WHEN (l.currency_id is not null AND l.amount_currency > 0.0)
                THEN sum(l.amount_currency)
                ELSE sum(l.debit)
            END as debit,
            CASE WHEN (l.currency_id is not null AND l.amount_currency < 0.0)
                THEN sum(l.amount_currency * (-1))
                ELSE sum(l.credit)
            END as credit,
            CASE WHEN l.date_maturity is null
                THEN l.date
                ELSE l.date_maturity
            END as date_maturity
            FROM account_move_line l
            JOIN account_account_type at ON (at.id = l.user_type_id)
            JOIN account_move m ON (l.move_id = m.id)
            WHERE l.partner_id IN (%s) AND (at.type = 'payable' OR at.type = 'receivable') 
                                AND '%s' < l.date AND l.date <= '%s'
            GROUP BY l.partner_id, m.name, l.date, l.date_maturity, l.name,
                                l.ref, l.blocked, l.currency_id,
                                l.amount_currency, l.company_id
        """ % (partners, date_start, date_end)

    def _display_lines_sql_q2(self, company_id):
        return """
            SELECT Q1.partner_id, move_id, date, date_maturity, Q1.name, ref,
                            debit, credit, debit-credit as amount, blocked,
            COALESCE(Q1.currency_id, c.currency_id) AS currency_id
            FROM Q1
            JOIN res_company c ON (c.id = Q1.company_id)
            WHERE c.id = %s
        """ % company_id
    def _display_lines_sql_q2_payable(self, company_id):
        return """
            SELECT Q1.partner_id, move_id, date, date_maturity, Q1.name, ref,
                            debit, credit, debit-credit as amount, blocked,
            COALESCE(Q1.currency_id, c.currency_id) AS currency_id
            FROM Q1
            JOIN res_company c ON (c.id = Q1.company_id)
            WHERE c.id = %s
        """ % company_id
    def _display_lines_sql_q2_receivable_and_payable(self, company_id):
        return """
            SELECT Q1.partner_id, move_id, date, date_maturity, Q1.name, ref,
                            debit, credit, debit-credit as amount, blocked,
            COALESCE(Q1.currency_id, c.currency_id) AS currency_id
            FROM Q1
            JOIN res_company c ON (c.id = Q1.company_id)
            WHERE c.id = %s
        """ % company_id

    def _get_account_display_lines(self, company_id, partner_ids, date_start,
                                   date_end):
        res = dict(map(lambda x: (x, []), partner_ids))
        partners = ', '.join([str(i) for i in partner_ids])
        date_start = datetime.strptime(
            date_start, DEFAULT_SERVER_DATE_FORMAT).date()
        date_end = datetime.strptime(
            date_end, DEFAULT_SERVER_DATE_FORMAT).date()
        self.env.cr.execute("""WITH Q1 AS (%s), Q2 AS (%s)
        SELECT partner_id, move_id, date, date_maturity, name, ref, debit,
                            credit, amount, blocked, currency_id
        FROM Q2
        ORDER BY date, date_maturity, move_id""" % (
            self._display_lines_sql_q1(partners, date_start, date_end),
            self._display_lines_sql_q2(company_id)))
        for row in self.env.cr.dictfetchall():
            res[row.pop('partner_id')].append(row)
        return res
    def _get_account_display_lines_payable(self, company_id, partner_ids, date_start,
                                   date_end):
        res = dict(map(lambda x: (x, []), partner_ids))
        partners = ', '.join([str(i) for i in partner_ids])
        date_start = datetime.strptime(
            date_start, DEFAULT_SERVER_DATE_FORMAT).date()
        date_end = datetime.strptime(
            date_end, DEFAULT_SERVER_DATE_FORMAT).date()
        self.env.cr.execute("""WITH Q1 AS (%s), Q2 AS (%s)
        SELECT partner_id, move_id, date, date_maturity, name, ref, debit,
                            credit, amount, blocked, currency_id
        FROM Q2
        ORDER BY date, date_maturity, move_id""" % (
            self._display_lines_sql_q1_payable(partners, date_start, date_end),
            self._display_lines_sql_q2_payable(company_id)))
        for row in self.env.cr.dictfetchall():
            res[row.pop('partner_id')].append(row)
        return res
    def _get_account_display_lines_receivable_and_payable(self, company_id, partner_ids, date_start,
                                   date_end):
        res = dict(map(lambda x: (x, []), partner_ids))
        partners = ', '.join([str(i) for i in partner_ids])
        date_start = datetime.strptime(
            date_start, DEFAULT_SERVER_DATE_FORMAT).date()
        date_end = datetime.strptime(
            date_end, DEFAULT_SERVER_DATE_FORMAT).date()
        self.env.cr.execute("""WITH Q1 AS (%s), Q2 AS (%s)
        SELECT partner_id, move_id, date, date_maturity, name, ref, debit,
                            credit, amount, blocked, currency_id
        FROM Q2
        ORDER BY date, date_maturity, move_id""" % (
            self._display_lines_sql_q1_receivable_and_payable(partners, date_start, date_end),
            self._display_lines_sql_q2_receivable_and_payable(company_id)))
        for row in self.env.cr.dictfetchall():
            res[row.pop('partner_id')].append(row)
        return res

    def _show_buckets_sql_q1(self, partners, date_end):
        return """
            SELECT l.partner_id, l.currency_id, l.company_id, l.move_id,
            CASE WHEN l.balance > 0.0
                THEN l.balance - sum(coalesce(pd.amount, 0.0))
                ELSE l.balance + sum(coalesce(pc.amount, 0.0))
            END AS open_due,
            CASE WHEN l.balance > 0.0
                THEN l.amount_currency - sum(coalesce(pd.amount_currency, 0.0))
                ELSE l.amount_currency + sum(coalesce(pc.amount_currency, 0.0))
            END AS open_due_currency,
            CASE WHEN l.date_maturity is null
                THEN l.date
                ELSE l.date_maturity
            END as date_maturity
            FROM account_move_line l
            JOIN account_account_type at ON (at.id = l.user_type_id)
            JOIN account_move m ON (l.move_id = m.id)
            LEFT JOIN (SELECT pr.*
                FROM account_partial_reconcile pr
                INNER JOIN account_move_line l2
                ON pr.credit_move_id = l2.id
                WHERE l2.date <= '%s'
            ) as pd ON pd.debit_move_id = l.id
            LEFT JOIN (SELECT pr.*
                FROM account_partial_reconcile pr
                INNER JOIN account_move_line l2
                ON pr.debit_move_id = l2.id
                WHERE l2.date <= '%s'
            ) as pc ON pc.credit_move_id = l.id
            WHERE l.partner_id IN (%s) AND at.type = 'receivable'
                                AND not l.reconciled AND not l.blocked
            GROUP BY l.partner_id, l.currency_id, l.date, l.date_maturity,
                                l.amount_currency, l.balance, l.move_id,
                                l.company_id
        """ % (date_end, date_end, partners)
    def _show_buckets_sql_q1_payable(self, partners, date_end):
        return """
            SELECT l.partner_id, l.currency_id, l.company_id, l.move_id,
            CASE WHEN l.balance > 0.0
                THEN l.balance - sum(coalesce(pd.amount, 0.0))
                ELSE l.balance + sum(coalesce(pc.amount, 0.0))
            END AS open_due,
            CASE WHEN l.balance > 0.0
                THEN l.amount_currency - sum(coalesce(pd.amount_currency, 0.0))
                ELSE l.amount_currency + sum(coalesce(pc.amount_currency, 0.0))
            END AS open_due_currency,
            CASE WHEN l.date_maturity is null
                THEN l.date
                ELSE l.date_maturity
            END as date_maturity
            FROM account_move_line l
            JOIN account_account_type at ON (at.id = l.user_type_id)
            JOIN account_move m ON (l.move_id = m.id)
            LEFT JOIN (SELECT pr.*
                FROM account_partial_reconcile pr
                INNER JOIN account_move_line l2
                ON pr.credit_move_id = l2.id
                WHERE l2.date <= '%s'
            ) as pd ON pd.debit_move_id = l.id
            LEFT JOIN (SELECT pr.*
                FROM account_partial_reconcile pr
                INNER JOIN account_move_line l2
                ON pr.debit_move_id = l2.id
                WHERE l2.date <= '%s'
            ) as pc ON pc.credit_move_id = l.id
            WHERE l.partner_id IN (%s) AND at.type = 'payable'
                                AND not l.reconciled AND not l.blocked
            GROUP BY l.partner_id, l.currency_id, l.date, l.date_maturity,
                                l.amount_currency, l.balance, l.move_id,
                                l.company_id
        """ % (date_end, date_end, partners)
    def _show_buckets_sql_q1_receivable_and_payable(self, partners, date_end):
        return """
            SELECT l.partner_id, l.currency_id, l.company_id, l.move_id,
            CASE WHEN l.balance > 0.0
                THEN l.balance - sum(coalesce(pd.amount, 0.0))
                ELSE l.balance + sum(coalesce(pc.amount, 0.0))
            END AS open_due,
            CASE WHEN l.balance > 0.0
                THEN l.amount_currency - sum(coalesce(pd.amount_currency, 0.0))
                ELSE l.amount_currency + sum(coalesce(pc.amount_currency, 0.0))
            END AS open_due_currency,
            CASE WHEN l.date_maturity is null
                THEN l.date
                ELSE l.date_maturity
            END as date_maturity
            FROM account_move_line l
            JOIN account_account_type at ON (at.id = l.user_type_id)
            JOIN account_move m ON (l.move_id = m.id)
            LEFT JOIN (SELECT pr.*
                FROM account_partial_reconcile pr
                INNER JOIN account_move_line l2
                ON pr.credit_move_id = l2.id
                WHERE l2.date <= '%s'
            ) as pd ON pd.debit_move_id = l.id
            LEFT JOIN (SELECT pr.*
                FROM account_partial_reconcile pr
                INNER JOIN account_move_line l2
                ON pr.debit_move_id = l2.id
                WHERE l2.date <= '%s'
            ) as pc ON pc.credit_move_id = l.id
            WHERE l.partner_id IN (%s) AND (at.type = 'payable' OR at.type = 'receivable')
                                AND not l.reconciled AND not l.blocked
            GROUP BY l.partner_id, l.currency_id, l.date, l.date_maturity,
                                l.amount_currency, l.balance, l.move_id,
                                l.company_id
        """ % (date_end, date_end, partners)

    def _show_buckets_sql_q2(self, today, minus_30, minus_60, minus_90,
                             minus_120):
        return """
            SELECT partner_id, currency_id, date_maturity, open_due,
                            open_due_currency, move_id, company_id,
            CASE
                WHEN '%s' <= date_maturity AND currency_id is null
                                THEN open_due
                WHEN '%s' <= date_maturity AND currency_id is not null
                                THEN open_due_currency
                ELSE 0.0
            END as current,
            CASE
                WHEN '%s' < date_maturity AND date_maturity < '%s'
                                AND currency_id is null THEN open_due
                WHEN '%s' < date_maturity AND date_maturity < '%s'
                                AND currency_id is not null
                                THEN open_due_currency
                ELSE 0.0
            END as b_1_30,
            CASE
                WHEN '%s' < date_maturity AND date_maturity <= '%s'
                                AND currency_id is null THEN open_due
                WHEN '%s' < date_maturity AND date_maturity <= '%s'
                                AND currency_id is not null
                                THEN open_due_currency
                ELSE 0.0
            END as b_30_60,
            CASE
                WHEN '%s' < date_maturity AND date_maturity <= '%s'
                                AND currency_id is null THEN open_due
                WHEN '%s' < date_maturity AND date_maturity <= '%s'
                                AND currency_id is not null
                                THEN open_due_currency
                ELSE 0.0
            END as b_60_90,
            CASE
                WHEN '%s' < date_maturity AND date_maturity <= '%s'
                                AND currency_id is null THEN open_due
                WHEN '%s' < date_maturity AND date_maturity <= '%s'
                                AND currency_id is not null
                                THEN open_due_currency
                ELSE 0.0
            END as b_90_120,
            CASE
                WHEN date_maturity <= '%s' AND currency_id is null
                                THEN open_due
                WHEN date_maturity <= '%s' AND currency_id is not null
                                THEN open_due_currency
                ELSE 0.0
            END as b_over_120
            FROM Q1
            GROUP BY partner_id, currency_id, date_maturity, open_due,
                                open_due_currency, move_id, company_id
        """ % (today, today, minus_30, today, minus_30, today, minus_60,
               minus_30, minus_60, minus_30, minus_90, minus_60, minus_90,
               minus_60, minus_120, minus_90, minus_120, minus_90, minus_120,
               minus_120)
    def _show_buckets_sql_q2_payable(self, today, minus_30, minus_60, minus_90,
                             minus_120):
        return """
            SELECT partner_id, currency_id, date_maturity, open_due,
                            open_due_currency, move_id, company_id,
            CASE
                WHEN '%s' <= date_maturity AND currency_id is null
                                THEN open_due
                WHEN '%s' <= date_maturity AND currency_id is not null
                                THEN open_due_currency
                ELSE 0.0
            END as current,
            CASE
                WHEN '%s' < date_maturity AND date_maturity < '%s'
                                AND currency_id is null THEN open_due
                WHEN '%s' < date_maturity AND date_maturity < '%s'
                                AND currency_id is not null
                                THEN open_due_currency
                ELSE 0.0
            END as b_1_30,
            CASE
                WHEN '%s' < date_maturity AND date_maturity <= '%s'
                                AND currency_id is null THEN open_due
                WHEN '%s' < date_maturity AND date_maturity <= '%s'
                                AND currency_id is not null
                                THEN open_due_currency
                ELSE 0.0
            END as b_30_60,
            CASE
                WHEN '%s' < date_maturity AND date_maturity <= '%s'
                                AND currency_id is null THEN open_due
                WHEN '%s' < date_maturity AND date_maturity <= '%s'
                                AND currency_id is not null
                                THEN open_due_currency
                ELSE 0.0
            END as b_60_90,
            CASE
                WHEN '%s' < date_maturity AND date_maturity <= '%s'
                                AND currency_id is null THEN open_due
                WHEN '%s' < date_maturity AND date_maturity <= '%s'
                                AND currency_id is not null
                                THEN open_due_currency
                ELSE 0.0
            END as b_90_120,
            CASE
                WHEN date_maturity <= '%s' AND currency_id is null
                                THEN open_due
                WHEN date_maturity <= '%s' AND currency_id is not null
                                THEN open_due_currency
                ELSE 0.0
            END as b_over_120
            FROM Q1
            GROUP BY partner_id, currency_id, date_maturity, open_due,
                                open_due_currency, move_id, company_id
        """ % (today, today, minus_30, today, minus_30, today, minus_60,
               minus_30, minus_60, minus_30, minus_90, minus_60, minus_90,
               minus_60, minus_120, minus_90, minus_120, minus_90, minus_120,
               minus_120)
    def _show_buckets_sql_q2_receivable_and_payable(self, today, minus_30, minus_60, minus_90,
                             minus_120):
        return """
            SELECT partner_id, currency_id, date_maturity, open_due,
                            open_due_currency, move_id, company_id,
            CASE
                WHEN '%s' <= date_maturity AND currency_id is null
                                THEN open_due
                WHEN '%s' <= date_maturity AND currency_id is not null
                                THEN open_due_currency
                ELSE 0.0
            END as current,
            CASE
                WHEN '%s' < date_maturity AND date_maturity < '%s'
                                AND currency_id is null THEN open_due
                WHEN '%s' < date_maturity AND date_maturity < '%s'
                                AND currency_id is not null
                                THEN open_due_currency
                ELSE 0.0
            END as b_1_30,
            CASE
                WHEN '%s' < date_maturity AND date_maturity <= '%s'
                                AND currency_id is null THEN open_due
                WHEN '%s' < date_maturity AND date_maturity <= '%s'
                                AND currency_id is not null
                                THEN open_due_currency
                ELSE 0.0
            END as b_30_60,
            CASE
                WHEN '%s' < date_maturity AND date_maturity <= '%s'
                                AND currency_id is null THEN open_due
                WHEN '%s' < date_maturity AND date_maturity <= '%s'
                                AND currency_id is not null
                                THEN open_due_currency
                ELSE 0.0
            END as b_60_90,
            CASE
                WHEN '%s' < date_maturity AND date_maturity <= '%s'
                                AND currency_id is null THEN open_due
                WHEN '%s' < date_maturity AND date_maturity <= '%s'
                                AND currency_id is not null
                                THEN open_due_currency
                ELSE 0.0
            END as b_90_120,
            CASE
                WHEN date_maturity <= '%s' AND currency_id is null
                                THEN open_due
                WHEN date_maturity <= '%s' AND currency_id is not null
                                THEN open_due_currency
                ELSE 0.0
            END as b_over_120
            FROM Q1
            GROUP BY partner_id, currency_id, date_maturity, open_due,
                                open_due_currency, move_id, company_id
        """ % (today, today, minus_30, today, minus_30, today, minus_60,
               minus_30, minus_60, minus_30, minus_90, minus_60, minus_90,
               minus_60, minus_120, minus_90, minus_120, minus_90, minus_120,
               minus_120)

    def _show_buckets_sql_q3(self, company_id):
        return """
            SELECT Q2.partner_id, current, b_1_30, b_30_60, b_60_90, b_90_120,
                                b_over_120,
            COALESCE(Q2.currency_id, c.currency_id) AS currency_id
            FROM Q2
            JOIN res_company c ON (c.id = Q2.company_id)
            WHERE c.id = %s
        """ % company_id
    def _show_buckets_sql_q3_payable(self, company_id):
        return """
            SELECT Q2.partner_id, current, b_1_30, b_30_60, b_60_90, b_90_120,
                                b_over_120,
            COALESCE(Q2.currency_id, c.currency_id) AS currency_id
            FROM Q2
            JOIN res_company c ON (c.id = Q2.company_id)
            WHERE c.id = %s
        """ % company_id
    def _show_buckets_sql_q3_receivable_and_payable(self, company_id):
        return """
            SELECT Q2.partner_id, current, b_1_30, b_30_60, b_60_90, b_90_120,
                                b_over_120,
            COALESCE(Q2.currency_id, c.currency_id) AS currency_id
            FROM Q2
            JOIN res_company c ON (c.id = Q2.company_id)
            WHERE c.id = %s
        """ % company_id

    def _show_buckets_sql_q4(self):
        return """
            SELECT partner_id, currency_id, sum(current) as current,
                                sum(b_1_30) as b_1_30,
                                sum(b_30_60) as b_30_60,
                                sum(b_60_90) as b_60_90,
                                sum(b_90_120) as b_90_120,
                                sum(b_over_120) as b_over_120
            FROM Q3
            GROUP BY partner_id, currency_id
        """
    def _show_buckets_sql_q4_payable(self):
        return """
            SELECT partner_id, currency_id, sum(current) as current,
                                sum(b_1_30) as b_1_30,
                                sum(b_30_60) as b_30_60,
                                sum(b_60_90) as b_60_90,
                                sum(b_90_120) as b_90_120,
                                sum(b_over_120) as b_over_120
            FROM Q3
            GROUP BY partner_id, currency_id
        """
    def _show_buckets_sql_q4_receivable_and_payable(self):
        return """
            SELECT partner_id, currency_id, sum(current) as current,
                                sum(b_1_30) as b_1_30,
                                sum(b_30_60) as b_30_60,
                                sum(b_60_90) as b_60_90,
                                sum(b_90_120) as b_90_120,
                                sum(b_over_120) as b_over_120
            FROM Q3
            GROUP BY partner_id, currency_id
        """

    _bucket_dates = {
        'today': fields.date.today(),
        'minus_30': fields.date.today() - timedelta(days=30),
        'minus_60': fields.date.today() - timedelta(days=60),
        'minus_90': fields.date.today() - timedelta(days=90),
        'minus_120': fields.date.today() - timedelta(days=120),
    }

    def _get_account_show_buckets(self, company_id, partner_ids, date_end):
        res = dict(map(lambda x: (x, []), partner_ids))
        partners = ', '.join([str(i) for i in partner_ids])
        date_end = datetime.strptime(
            date_end, DEFAULT_SERVER_DATE_FORMAT).date()
        self.env.cr.execute("""WITH Q1 AS (%s), Q2 AS (%s),
        Q3 AS (%s), Q4 AS (%s)
        SELECT partner_id, currency_id, current, b_1_30, b_30_60, b_60_90,
                            b_90_120, b_over_120,
                            current+b_1_30+b_30_60+b_60_90+b_90_120+b_over_120
                            AS balance
        FROM Q4
        GROUP BY partner_id, currency_id, current, b_1_30, b_30_60, b_60_90,
        b_90_120, b_over_120""" % (
            self._show_buckets_sql_q1(partners, date_end),
            self._show_buckets_sql_q2(
                self._bucket_dates['today'],
                self._bucket_dates['minus_30'],
                self._bucket_dates['minus_60'],
                self._bucket_dates['minus_90'],
                self._bucket_dates['minus_120']),
            self._show_buckets_sql_q3(company_id),
            self._show_buckets_sql_q4()))
        for row in self.env.cr.dictfetchall():
            res[row.pop('partner_id')].append(row)
        return res
    def _get_account_show_buckets_payable(self, company_id, partner_ids, date_end):
        res = dict(map(lambda x: (x, []), partner_ids))
        partners = ', '.join([str(i) for i in partner_ids])
        date_end = datetime.strptime(
            date_end, DEFAULT_SERVER_DATE_FORMAT).date()
        self.env.cr.execute("""WITH Q1 AS (%s), Q2 AS (%s),
        Q3 AS (%s), Q4 AS (%s)
        SELECT partner_id, currency_id, current, b_1_30, b_30_60, b_60_90,
                            b_90_120, b_over_120,
                            current+b_1_30+b_30_60+b_60_90+b_90_120+b_over_120
                            AS balance
        FROM Q4
        GROUP BY partner_id, currency_id, current, b_1_30, b_30_60, b_60_90,
        b_90_120, b_over_120""" % (
            self._show_buckets_sql_q1_payable(partners, date_end),
            self._show_buckets_sql_q2_payable(
                self._bucket_dates['today'],
                self._bucket_dates['minus_30'],
                self._bucket_dates['minus_60'],
                self._bucket_dates['minus_90'],
                self._bucket_dates['minus_120']),
            self._show_buckets_sql_q3_payable(company_id),
            self._show_buckets_sql_q4_payable()))
        for row in self.env.cr.dictfetchall():
            res[row.pop('partner_id')].append(row)
        return res

    def _get_account_show_buckets_receivable_and_payable(self, company_id, partner_ids, date_end):
        res = dict(map(lambda x: (x, []), partner_ids))
        partners = ', '.join([str(i) for i in partner_ids])
        date_end = datetime.strptime(
            date_end, DEFAULT_SERVER_DATE_FORMAT).date()
        self.env.cr.execute("""WITH Q1 AS (%s), Q2 AS (%s),
        Q3 AS (%s), Q4 AS (%s)
        SELECT partner_id, currency_id, current, b_1_30, b_30_60, b_60_90,
                            b_90_120, b_over_120,
                            current+b_1_30+b_30_60+b_60_90+b_90_120+b_over_120
                            AS balance
        FROM Q4
        GROUP BY partner_id, currency_id, current, b_1_30, b_30_60, b_60_90,
        b_90_120, b_over_120""" % (
            self._show_buckets_sql_q1_receivable_and_payable(partners, date_end),
            self._show_buckets_sql_q2_receivable_and_payable(
                self._bucket_dates['today'],
                self._bucket_dates['minus_30'],
                self._bucket_dates['minus_60'],
                self._bucket_dates['minus_90'],
                self._bucket_dates['minus_120']),
            self._show_buckets_sql_q3_receivable_and_payable(company_id),
            self._show_buckets_sql_q4_receivable_and_payable()))
        for row in self.env.cr.dictfetchall():
            res[row.pop('partner_id')].append(row)
        return res

    @api.multi
    def render_html(self, docids,data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        company_id = data['company_id']
        partner_ids = data['partner_ids']
        date_start = data['date_start']
        date_end = data['date_end']
        today = fields.Date.today()
        if data['report_type'] == 'receivable':
            balance_start_to_display, buckets_to_display = {}, {}
            lines_to_display, amount_due = {}, {}
            currency_to_display = {}
            today_display, date_start_display, date_end_display = {}, {}, {}

            balance_start = self._get_account_initial_balance(
                company_id, partner_ids, date_start)

            for partner_id in partner_ids:
                balance_start_to_display[partner_id] = {}
                for line in balance_start[partner_id]:
                    currency = self.env['res.currency'].browse(line['currency_id'])
                    if currency not in balance_start_to_display[partner_id]:
                        balance_start_to_display[partner_id][currency] = []
                    balance_start_to_display[partner_id][currency] = \
                        line['balance']

            lines = self._get_account_display_lines(
                company_id, partner_ids, date_start, date_end)

            for partner_id in partner_ids:
                lines_to_display[partner_id], amount_due[partner_id] = {}, {}
                currency_to_display[partner_id] = {}
                today_display[partner_id] = self._format_date_to_partner_lang(
                    today, partner_id)
                date_start_display[partner_id] = self._format_date_to_partner_lang(
                    date_start, partner_id)
                date_end_display[partner_id] = self._format_date_to_partner_lang(
                    date_end, partner_id)
                for line in lines[partner_id]:
                    currency = self.env['res.currency'].browse(line['currency_id'])
                    if currency not in lines_to_display[partner_id]:
                        lines_to_display[partner_id][currency] = []
                        currency_to_display[partner_id][currency] = currency
                        if currency in balance_start_to_display[partner_id]:
                            amount_due[partner_id][currency] = \
                                balance_start_to_display[partner_id][currency]
                        else:
                            amount_due[partner_id][currency] = 0.0
                    if not line['blocked']:
                        amount_due[partner_id][currency] += line['amount']
                    line['balance'] = amount_due[partner_id][currency]
                    line['date'] = self._format_date_to_partner_lang(
                        line['date'], partner_id)
                    line['date_maturity'] = self._format_date_to_partner_lang(
                        line['date_maturity'], partner_id)
                    lines_to_display[partner_id][currency].append(line)

            if data['show_aging_buckets']:
                buckets = self._get_account_show_buckets(
                    company_id, partner_ids, date_end)
                for partner_id in partner_ids:
                    buckets_to_display[partner_id] = {}
                    for line in buckets[partner_id]:
                        currency = self.env['res.currency'].browse(
                            line['currency_id'])
                        if currency not in buckets_to_display[partner_id]:
                            buckets_to_display[partner_id][currency] = []
                        buckets_to_display[partner_id][currency] = line

        if data['report_type'] == 'payable':
            balance_start_to_display, buckets_to_display = {}, {}
            lines_to_display, amount_due = {}, {}
            currency_to_display = {}
            today_display, date_start_display, date_end_display = {}, {}, {}

            balance_start = self._get_account_initial_balance_payable(
                company_id, partner_ids, date_start)

            for partner_id in partner_ids:
                balance_start_to_display[partner_id] = {}
                for line in balance_start[partner_id]:
                    currency = self.env['res.currency'].browse(line['currency_id'])
                    if currency not in balance_start_to_display[partner_id]:
                        balance_start_to_display[partner_id][currency] = []
                    balance_start_to_display[partner_id][currency] = \
                        line['balance']

            lines = self._get_account_display_lines_payable(
                company_id, partner_ids, date_start, date_end)

            for partner_id in partner_ids:
                lines_to_display[partner_id], amount_due[partner_id] = {}, {}
                currency_to_display[partner_id] = {}
                today_display[partner_id] = self._format_date_to_partner_lang(
                    today, partner_id)
                date_start_display[partner_id] = self._format_date_to_partner_lang(
                    date_start, partner_id)
                date_end_display[partner_id] = self._format_date_to_partner_lang(
                    date_end, partner_id)
                for line in lines[partner_id]:
                    currency = self.env['res.currency'].browse(line['currency_id'])
                    if currency not in lines_to_display[partner_id]:
                        lines_to_display[partner_id][currency] = []
                        currency_to_display[partner_id][currency] = currency
                        if currency in balance_start_to_display[partner_id]:
                            amount_due[partner_id][currency] = \
                                balance_start_to_display[partner_id][currency]
                        else:
                            amount_due[partner_id][currency] = 0.0
                    if not line['blocked']:
                        amount_due[partner_id][currency] += line['amount']
                    line['balance'] = amount_due[partner_id][currency]
                    line['date'] = self._format_date_to_partner_lang(
                        line['date'], partner_id)
                    line['date_maturity'] = self._format_date_to_partner_lang(
                        line['date_maturity'], partner_id)
                    lines_to_display[partner_id][currency].append(line)

            if data['show_aging_buckets']:
                buckets = self._get_account_show_buckets_payable(
                    company_id, partner_ids, date_end)
                for partner_id in partner_ids:
                    buckets_to_display[partner_id] = {}
                    for line in buckets[partner_id]:
                        currency = self.env['res.currency'].browse(
                            line['currency_id'])
                        if currency not in buckets_to_display[partner_id]:
                            buckets_to_display[partner_id][currency] = []
                        buckets_to_display[partner_id][currency] = line

        if data['report_type'] == 'receivable_and_payable':
            balance_start_to_display, buckets_to_display = {}, {}
            lines_to_display, amount_due = {}, {}
            currency_to_display = {}
            today_display, date_start_display, date_end_display = {}, {}, {}

            balance_start = self._get_account_initial_balance_receivable_and_payable(
                company_id, partner_ids, date_start)

            for partner_id in partner_ids:
                balance_start_to_display[partner_id] = {}
                for line in balance_start[partner_id]:
                    currency = self.env['res.currency'].browse(line['currency_id'])
                    if currency not in balance_start_to_display[partner_id]:
                        balance_start_to_display[partner_id][currency] = []
                    balance_start_to_display[partner_id][currency] = \
                        line['balance']

            lines = self._get_account_display_lines_receivable_and_payable(
                company_id, partner_ids, date_start, date_end)

            for partner_id in partner_ids:
                lines_to_display[partner_id], amount_due[partner_id] = {}, {}
                currency_to_display[partner_id] = {}
                today_display[partner_id] = self._format_date_to_partner_lang(
                    today, partner_id)
                date_start_display[partner_id] = self._format_date_to_partner_lang(
                    date_start, partner_id)
                date_end_display[partner_id] = self._format_date_to_partner_lang(
                    date_end, partner_id)
                for line in lines[partner_id]:
                    currency = self.env['res.currency'].browse(line['currency_id'])
                    if currency not in lines_to_display[partner_id]:
                        lines_to_display[partner_id][currency] = []
                        currency_to_display[partner_id][currency] = currency
                        if currency in balance_start_to_display[partner_id]:
                            amount_due[partner_id][currency] = \
                                balance_start_to_display[partner_id][currency]
                        else:
                            amount_due[partner_id][currency] = 0.0
                    if not line['blocked']:
                        amount_due[partner_id][currency] += line['amount']
                    line['balance'] = amount_due[partner_id][currency]
                    line['date'] = self._format_date_to_partner_lang(
                        line['date'], partner_id)
                    line['date_maturity'] = self._format_date_to_partner_lang(
                        line['date_maturity'], partner_id)
                    lines_to_display[partner_id][currency].append(line)

            if data['show_aging_buckets']:
                buckets = self._get_account_show_buckets_receivable_and_payable(
                    company_id, partner_ids, date_end)
                for partner_id in partner_ids:
                    buckets_to_display[partner_id] = {}
                    for line in buckets[partner_id]:
                        currency = self.env['res.currency'].browse(
                            line['currency_id'])
                        if currency not in buckets_to_display[partner_id]:
                            buckets_to_display[partner_id][currency] = []
                        buckets_to_display[partner_id][currency] = line
        payments = []
        Lines = []
        total_venda = 0
        total_pago = 0
        total_aberto = 0
        for partner_id in partner_ids:
            sale_lines = self.env['sale.order.line'].search([('partner_id','=', partner_id),
                                                             ('order_id.date_order','>=',date_start),
                                                             ('order_id.date_order','<=',date_end)
                                                             ])
            pos_lines = self.env['pos.order.line'].search([('partner_id','=', partner_id),
                                                           ('order_id.date_order','>=',date_start),
                                                           ('order_id.date_order','<=',date_end)
                                                           ])
            type_payment = ''
            type_payment = self.env['account.account.type'].search([('type','=','receivable')])
            # payments = []
            # Lines = []
            # total_venda = 0
            # total_pago = 0
            for s in sale_lines:
                map = self.env['medical.map'].search([('sale_order_line_id','=',s.id)])
                if map:
                    if len(map) == 1:
                        os = map.code
                        pet = map.patient_id.name
                    else:
                        os = map[0].code
                        pet = map[0].patient_id.name
                else:
                    if s.salon_order_id:
                        pet = s.salon_order_id.patient_id.name
                        os = s.salon_order_id.name
                    else:
                        os = ''
                        pet = ''
                if s.invoice_lines:
                    if len(s.invoice_lines) == 1:
                        if s.invoice_lines.invoice_id.state == 'paid':
                            state = 'Pago'
                        else:
                            state = 'Pendente'
                    else:
                        if s.invoice_lines[0].invoice_id.state == 'paid':
                            state = 'Pago'
                        else:
                            state = 'Pendente'
                else:
                    state = 'Pendente'

                sl = {
                 'date': '%s/%s/%s' % (s.order_id.date_order[8:-8],s.order_id.date_order[5:-12],s.order_id.date_order[:-15]),
                 'OS': os,
                 'pet': pet,
                 'fatura': s.order_id.name,
                 'produto': s.product_id.name,
                 'valor': ("%.2f" % s.price_subtotal).replace('.',','),
                 'status': state,
                }
                total_venda += s.price_subtotal
                Lines.append(sl)
            for p in pos_lines:
                if p.order_id.state in ['paid','done']:
                    state_pos = 'Pago'
                else:
                    state_pos = 'Pendente'
                pl = {
                'date': '%s/%s/%s' % (p.order_id.date_order[8:-8],p.order_id.date_order[5:-12],p.order_id.date_order[:-15]),
                'OS': '',
                'pet': '',
                'fatura': p.order_id.name,
                'produto': p.product_id.name,
                'valor': ("%.2f" % (p.price_unit * p.qty - p.discount_fixed - (((p.price_unit * p.qty) * p.discount) / 100))).replace('.',','),
                'status': state_pos,
                }
                total_venda += (p.price_unit * p.qty - p.discount_fixed - (((p.price_unit * p.qty) * p.discount) / 100))
                Lines.append(pl)
            pays = self.env['account.move.line'].search([('user_type_id', '=', type_payment.id),
                                                         ('partner_id', 'in', partner_ids),
                                                         ('credit', '=', 0)
                                                         ])
            for i in pays:
                pay_dict = {
                    'date': '%s/%s/%s' % (i.date_maturity[8:], i.date_maturity[5:-3], i.date_maturity[:-6]),
                    'valor': ("%.2f" % i.debit).replace('.', ',')
                }
                if i.reconciled:
                    total_pago += i.debit
                    payments.append(pay_dict)
                if i.account_id.name == u'Títulos a receber':
                    total_aberto += i.debit


        docargs = {
            'company': self.env['res.company'].browse(company_id),
            'doc_ids': partner_ids,
            'doc_model': 'res.partner',
            'docs': self.env['res.partner'].browse(partner_ids),
            'Amount_Due': amount_due,
            'Balance_forward': balance_start_to_display,
            'Lines': Lines,
            'Payments': payments,
            'total_venda': ("%.2f" % total_venda).replace('.',','),
            'total_pago': ("%.2f" % total_pago).replace('.',','),
            'total_saldo': ("%.2f" % (total_aberto-total_pago)).replace('.',','),
            'Buckets': buckets_to_display,
            'Currencies': currency_to_display,
            'Show_Buckets': data['show_aging_buckets'],
            'Filter_non_due_partners': data['filter_partners_non_due'],
            'Date_start': date_start_display,
            'Date_end': date_end_display,
            'Date': today_display,
        }
        return self.env['report'].render(
            'customer_statement.statement', values=docargs)
