# -*- coding: utf-8 -*-

from odoo import api, models

class ReporteKardex(models.AbstractModel):
    _name = 'report.kardex.reporte_kardex'

    def inicial(self, datos):

        self.env.cr.execute("select sum(qty_in) as entrada, sum(qty_out) as salida, product_id \
            from ( \
               select sum(product_qty) as qty_in, 0 as qty_out, product_id \
               from stock_move \
               where state = 'done' and product_id = %s and location_dest_id = %s and date <= %s \
               group by product_id \
               union \
               select 0 as qty_in, sum(product_qty) as qty_out, product_id \
               from stock_move \
               where state = 'done' and product_id = %s and  location_id = %s and date <= %s \
               group by product_id \
            ) movimientos\
            group by product_id",
            (datos['producto_id'][0], datos['ubicacion_id'][0], datos['fecha_desde'], datos['producto_id'][0], datos['ubicacion_id'][0], datos['fecha_desde']))
        lineas = self.env.cr.dictfetchall()

        self.env.cr.execute("select sum(qty) as reserva from stock_quant where product_id = %s and location_id = %s and in_date <= %s",
                            (datos['producto_id'][0], datos['ubicacion_id'][0], datos['fecha_desde']))
        line_quant = self.env.cr.dictfetchall()

        if not line_quant[0]['reserva']:
            reserva = 0
        else:
            reserva = line_quant[0]['reserva']
        total = 0
        for l in lineas:
            total += l['entrada'] - l['salida']

        return total - reserva

    def lineas(self, datos):
        totales = {}
        totales['entrada'] = 0
        totales['salida'] = 0
        totales['inicio'] = 0
        total = self.inicial(datos)
        if not total:
            total = 0
        totales['inicio'] = total

        saldo = totales['inicio']
        lineas = []
        q = 0
        reserva = 0
        for m in self.env['stock.move'].search([('product_id','=',datos['producto_id'][0]), ('date','>=',datos['fecha_desde']), ('date','<=',datos['fecha_hasta']), ('state','in',['done']), '|', ('location_id','=',datos['ubicacion_id'][0]), ('location_dest_id','=',datos['ubicacion_id'][0])], order = 'date'):
        #for m in self.env['stock.quant'].search([('product_id','=',datos['producto_id'][0]), ('in_date','>=',datos['fecha_desde']), ('in_date','<=',datos['fecha_hasta']), '|', ('location_id','=',datos['ubicacion_id'][0]), ('location_id','!=',datos['ubicacion_id'][0])], order = 'in_date'):
            r = 0
            for i in m.quant_ids:
                if i.location_id.id != datos['ubicacion_id'][0] and m.location_dest_id.id == datos['ubicacion_id'][0] and m.location_id.id != 9:
                    reserva += i.qty
                    r += i.qty
            detalle = {
                'empresa':'-',
                'fecha': m.date,
                'entrada': 0,
                'salida': 0,
                'saldo':saldo
            }

            if m.picking_id:
                detalle['documento'] = m.picking_id.name
                if m.picking_id.partner_id:
                    detalle['empresa'] = m.picking_id.partner_id.name

            else:
                detalle['documento'] = m.product_id.name

            if m.location_dest_id.id == datos['ubicacion_id'][0]:
                detalle['tipo'] = 'Ingreso'
                detalle['entrada'] = m.product_qty
                totales['entrada'] += m.product_qty
                # saldo += m.qty
                # detalle['costo'] = m.cost
            elif m.location_id.id == datos['ubicacion_id'][0]:
                detalle['tipo'] = 'Salida'
                detalle['salida'] = -m.product_qty
                totales['salida'] -= m.product_qty
                # saldo -= m.qty
                # detalle['costo'] = -m.cost

            saldo += detalle['entrada']+detalle['salida']
            detalle['saldo'] = saldo

            costo = m.product_id.get_history_price(m.company_id.id, date=m.date)
            detalle['costo'] = costo

            lineas.append(detalle)
        totales['reserva'] = reserva
        return {'lineas': lineas, 'totales': totales}

    @api.model
    def render_html(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_ids', []))

        docargs = {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'data': data['form'],
            'docs': docs,
            'lineas': self.lineas,
        }
        return self.env['report'].render('kardex.reporte_kardex', docargs)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
