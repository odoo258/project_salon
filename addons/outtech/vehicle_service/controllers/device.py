# -*- coding: utf-8 -*-
import logging
import requests as req
from odoo.http import request

from openerp import http
# import openerp.addons.web.http as http

_logger = logging.getLogger(__name__)

class DeviceController(http.Controller):
    _path = '/tracknme/device-control'
	
    @http.route(_path, auth='user')
    def index(self, **args):
        url = 'http://localhost/api/device-control/index.php'
        response = req.get(url)

        return response.text

    @http.route(_path + '/search', type='json', auth='user')
    def search(self, **args):
        inst = request.env['installation.schedule'].sudo().browse(int(args['taskId']))
        if inst.reseller_id:
            equip = request.env['stock.production.lot'].sudo().search([('name','=',args['serial_number'])])
            stock = request.env['stock.quant'].sudo().search([('qty','>',0),('location_id', 'in', [inst.reseller_id.resale_location.id]),('lot_id','=',equip.id)])
            if stock and equip:
                data = {
                    'DEVICE': equip.id
                }
                inst.write({'equipment_draft_id':equip.id})
                return data
            else:
                erro = u"Número de Série (%s) não localizado!" % (args['serial_number'])
                data = {
                    'ERROR': erro
                }
                return data
        else:
            erro = u"Nenhuma Revenda Selecionada para Instalação!"
            data = {
                'ERROR': erro
            }
            return data
            #return self.json_post('device-control/search.php', args)

    @http.route(_path + '/enable', type='json', auth='user')
    def enable(self, **args):
        inst = request.env['installation.schedule'].browse(int(args['taskId']))
        equip = request.env['stock.production.lot'].browse(args['deviceId'])
        partner = request.env['res.partner'].browse(inst.partner_id.id)
        if args:
            args.update({
                'product_id':equip.product_id.id,
                'user_plataforma':partner.user_plataforma,
                'name_product':equip.product_id.name,
                'sim_msisdn': equip.sim_msisdn,
                'imei': equip.imei,
                'sim_iccid': equip.sim_iccid,
                'model': equip.model,
                'sim_operator': equip.sim_operator,
                'identifier':equip.identifier
                         })
    	return self.json_post('device-control/enable.php', args)

    @http.route(_path + '/save_id', type='json', auth='user')
    def save_id(self, **args):
    	if 'equip' in args and 'deviceId' in args:
            equip_id = args['equip']
            deviceId = args['deviceId']
            equip = request.env['stock.production.lot'].browse(int(equip_id))
            equip.write({'id_plataforma':str(deviceId)})
    	    return True
        else:
            return False

    @http.route(_path + '/info', type='json', auth='user')
    def info(self, **args):
    	return self.json_post('device-control/info.php', args)


    def json_post(self, action, args):
        url = "http://localhost/api/%s" % action
        response = req.post(url, args)

        return response.json()
