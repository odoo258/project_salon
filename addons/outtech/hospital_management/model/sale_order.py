# coding=utf-8
# Author: Christian Douglas <christian.douglas.alcantara@gmail.com>

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    admission_id = fields.Many2one(
        'medical.inpatient.registration', string="Map"
    )

    @api.one
    def change_map_state(self, state):
        line_ids = self.order_line.ids
        admission = self.admission_id
        if admission:
            maps = admission.map_ids.search([
                ('sale_order_line_id', 'in', line_ids), ('admission_id', '=', admission.id)
            ])
            for omap in maps:
                omap.state = state
                omap.write({'sale_approved':'approved'})

    @api.multi
    def action_confirm(self):
        for order in self:
            # order.change_map_state('open_attendance')
            order.change_map_state('start_attendance')
        return super(SaleOrder, self).action_confirm()

    @api.multi
    def action_cancel(self):
        for order in self:
            # order.change_map_state('open')
            order.change_map_state('schedule')
        return super(SaleOrder, self).action_cancel()
