# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    check_ids = fields.One2many('quality.check', 'picking_id', 'Checks')
    check_todo = fields.Boolean('Pending checks', compute='_compute_check_todo')

    @api.one
    def _compute_check_todo(self):
        # TDE: measure_success use ?
        if any(check.quality_state == 'none' for check in self.check_ids):
            self.check_todo = True

    @api.multi
    def check_quality(self):
        self.ensure_one()
        checks = self.check_ids.filtered(lambda check: check.quality_state == 'none')
        if checks:
            action = self.env.ref('quality.quality_check_action_small').read()[0]
            action['context'] = self.env.context
            action['res_id'] = checks.ids[0]
            return action
        return False

    @api.multi
    def _create_backorder(self, backorder_moves=[]):
        res = super(StockPicking, self)._create_backorder(backorder_moves=backorder_moves)
        # Do not crash if Community was not updated
        if isinstance(res, bool):
            return res

        # Transfer the quality checks from the original picking to the backorder
        for backorder in res:
            backorder.backorder_id.check_ids.filtered(lambda x: x.quality_state == 'none').write({
                'picking_id': backorder.id,
            })
        return res

    @api.multi
    def do_transfer(self):
        # Do the check before transferring
        if self.mapped('check_ids').filtered(lambda x: x.quality_state == 'none'):
            raise UserError(_('You still need to do the quality checks!'))
        return super(StockPicking, self).do_transfer()
