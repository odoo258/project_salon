# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api, _
import requests as req
from odoo.http import request
from openerp import http
from dateutil import relativedelta
from datetime import date
from odoo.exceptions import UserError


_logger = logging.getLogger(__name__)

class TracknmeController(http.Controller):
	
    @http.route('/tracknme/', auth='user')
    def index(self, **args):
        url = 'http://localhost/api/device-control/index.php'
        response = req.get(url)

        return response.text

    @http.route('/tracknme/admin-sell', auth='user')
    def admin_sell(self, **args):
        url = 'http://localhost/api/admin-sell/index.php'
        response = req.get(url)

        return response.text

    @http.route('/tracknme/contract/active', type='json', auth='user')
    def active(self, **args):
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        args.update({'msg':'', 'contract_id':''})
        if not args['serial_number']:
            args['msg'] = 'Sem Equipamento Cadastrado!'
            return self.json_post('contract/active.php', args)
        inst = request.env['installation.schedule'].browse(int(args['taskId']))
        company = self.env['res.company'].browse(1)
        url = company.url_api + '/api/trackings?by=device&device=%s&limit=1' % self.equipment_id.id_plataforma
        info = req.get(url, headers=headers)
        if info.status_code in [200,201]:
            res_info = eval(info.text)
            content = res_info['content'][0]
            if not content['valid'] or not content['latitude'] or not content['longitude'] or not content['sensors']:
                raise UserError(_(u'Não é porssivel ativar contrato sem finalizar os testes de Equipamentos!'))
        if inst.sale_order_id:
            picking_type = False
            lot = request.env['stock.production.lot'].search([('name','=',args['serial_number'])])
            picking = request.env['stock.picking'].search([('state','!=','done'),('sale_id','=',inst.sale_order_id.id),('location_dest_id','=',9)])
            if not picking:
                type = request.env['stock.picking.type'].search([('default_location_src_id','=',inst.reseller_id.resale_location.id),
                                                                 ('code','=','outgoing')])
                dict_p = {

                    'partner_id': inst.partner_id.id,
                    'location_id': inst.reseller_id.resale_location.id,
                    'location_dest_id': 9,
                    'picking_type_id': type[0].id
                }
                picking = request.env['stock.picking'].create(dict_p)

                dict_line_p = {

                    'name': inst.name,
                    'origin': inst.name,
                    'product_id': lot.product_id.id,
                    'product_uom': lot.product_id.uom_id.id,
                    'product_uom_qty': 1,
                    'location_id': inst.reseller_id.resale_location.id,
                    'location_dest_id': 9,
                    'restrict_lot_id': lot.id,
                    'picking_id': picking.id

                }
                request.env['stock.move'].create(dict_line_p)
            if picking and inst.reseller_id:

                picking.action_confirm()
                picking.do_transfer()
            else:
                args['msg'] = 'Sem Revendedor Cadastrado!'
        if inst.contract_id:
            if inst.contract_id.state != 'draft':
                args['msg'] = 'Contrato ja Ativo!'
            else:
                date_new = date.today() + relativedelta.relativedelta(days=30)
                request.env['sale.subscription'].sudo().browse(inst.contract_id.id).sudo().set_open()
                request.env['sale.subscription'].sudo().browse(inst.contract_id.id).sudo().write({'recurring_next_date': date_new})
                args.update({'contract_id':inst.contract_id.id})
                inst.write({'equipment_id':lot.id,'state':'activated'})
                quick_sale = request.env['quick.sale'].search([('installation_id','=',inst.id)])
                if quick_sale:
                    quick_sale.write({'state':'done'})
            return self.json_post('contract/active.php', args)
        else:
            args['msg'] = 'Sem contrato definido!'
            return self.json_post('contract/active.php', args)

    def json_post(self, action, args):
        url = "http://localhost/api/%s" % action
        response = req.post(url, args)

        return response.json()

#     @http.route('/tracknme/tracknme/objects/', auth='user')
#     def list(self, **args):
#         return http.request.render('tracknme.listing', {
#             'root': '/tracknme/tracknme',
#             'objects': http.request.env['tracknme.tracknme'].search([]),
#         })

#     @http.route('/tracknme/tracknme/objects/<model("tracknme.tracknme"):obj>/', auth='user')
#     def object(self, obj, **args):
#         return http.request.render('tracknme.object', {
#             'object': obj
#         })