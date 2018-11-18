# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.tools import ustr
from odoo.exceptions import UserError

# ---------------------------------------------------------
# Budgets
# ---------------------------------------------------------
class CrossoveredBudgetLines(models.Model):
    _inherit = "crossovered.budget.lines"

    residual_amount = fields.Float(string='Valor Residual', digits=0)


    @api.multi
    def _compute_practical_amount(self):
        for line in self:
            result = 0.0
            acc_ids = line.general_budget_id.account_ids.ids
            if not acc_ids:
                raise UserError(_("The Budget '%s' has no accounts!") % ustr(line.general_budget_id.name))
            date_to = self.env.context.get('wizard_date_to') or line.date_to
            date_from = self.env.context.get('wizard_date_from') or line.date_from
            if line.analytic_account_id.id:
                self.env.cr.execute("""
                    SELECT SUM(amount)
                    FROM account_analytic_line
                    WHERE account_id=%s
                        AND (date between to_date(%s,'yyyy-mm-dd') AND to_date(%s,'yyyy-mm-dd'))
                        AND general_account_id=ANY(%s)""",
                (line.analytic_account_id.id, date_from, date_to, acc_ids,))
                result = self.env.cr.fetchone()[0] or 0.0
            else:
                self.env.cr.execute("""
                    SELECT SUM(credit)
                    FROM account_move_line
                    WHERE (date between to_date(%s,'yyyy-mm-dd') AND to_date(%s,'yyyy-mm-dd'))
                        AND account_id=ANY(%s)""",
                (date_from, date_to, acc_ids,))
                credit = self.env.cr.fetchone()[0] or 0.0
                self.env.cr.execute("""
                    SELECT SUM(debit)
                    FROM account_move_line
                    WHERE (date between to_date(%s,'yyyy-mm-dd') AND to_date(%s,'yyyy-mm-dd'))
                        AND account_id=ANY(%s)""",
                (date_from, date_to, acc_ids,))
                debit = self.env.cr.fetchone()[0] or 0.0
                result = credit - debit

            residual = line.planned_amount - result
            line.practical_amount = result
            line.write({'residual_amount': residual})
