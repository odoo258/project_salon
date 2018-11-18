# coding=utf-8
# Author: Christian Douglas <christian.douglas.alcantara@gmail.com>
from odoo import models, fields, api, _
from odoo.exceptions import Warning


class MapQuotationWizard(models.TransientModel):
    _name = 'map.quotation.wizard'

    @api.model
    def _get_service_ids(self):
        reports = []
        if self._context.get('active_id'):
            admission = self.env['medical.inpatient.registration'].browse(self._context.get('active_id'))
            reports = admission.map_ids.search([
                # ('state', 'in', ['open', 'draft', 'schedule']),
                ('state', 'in', ['draft', 'schedule']),
                ('admission_id', '=', admission.id),
                ('sale_order_line_id', '=', False)
            ])
        return reports

    order_id = fields.Many2one(
        'sale.order', string='Sale Order'
    )
    service_ids = fields.Many2many(
        'medical.map', string="Services", required=True, default=_get_service_ids
    )

    @api.multi
    def make_quotation(self):
        if not self.service_ids:
            raise Warning(_('Select at least one Service.'))

        admission_id = self._context.get('active_id')
        medical_inpatient_registration = self.env['medical.inpatient.registration']
        mir = medical_inpatient_registration.browse(admission_id)

        sale_order = self.env['sale.order']
        if self.order_id:
            order = self.order_id
        else:
            order = sale_order.create({
                'partner_id': mir.owner_id.id,

            })
            order.admission_id = admission_id

        sale_order_line = self.env['sale.order.line']
        for service in self.service_ids:
            if not service.service_id:
                raise Warning(_("The OS %s don't have a service selected. Please choose one.") % service.code)
            product = service.service_id
            vals = {
                'price_unit': product.list_price,
                'product_uom': product.uom_id.id,
                'name': service.name,
                'order_id': order.id,
                'product_id': product.id,
            }
            sol = sale_order_line.create(vals)
            service.sale_order_line_id = sol.id
            #service.state = 'open'
            service.state = 'schedule'

