# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2017 - OutTech (<http://www.outtech.com.br>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields, api,  _

class ProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    identifier = fields.Char(string="ID")
    imei = fields.Char(string="IMEI", required=True)
    model = fields.Char(string="Model", required=True)
    version = fields.Char(string="Version")
    password = fields.Char(string="Password")
    sim_apn = fields.Char(string="APN")
    sim_iccid = fields.Char(string="ICCID", required=True)
    sim_imsi = fields.Char(string="IMSI")
    sim_msisdn = fields.Char(string="MSISDN", required=True)
    sim_operator = fields.Char(string="Operator", required=True)
    sim_password = fields.Char(string="Password")
    sim_length_plan = fields.Char(string="Length Plan")
    sim_user = fields.Char(string="User")
    id_plataforma = fields.Char(string='ID Plataforma', readonly=True)



    @api.onchange('sim_iccid')
    def sim_iccid_change(self):

        if self.sim_iccid:
            if len(self.sim_iccid) != 20:
                return {'warning': {'title': _('WARNING'), 'message': _('Invalid Number SIM ICCID!')}}
        return {'value':{'sim_iccid':self.sim_iccid}}

class StockLocation(models.Model):
    _inherit = 'stock.location'

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        if 'uid' in self._context:
            user = self.env['res.users'].browse(self._context['uid'])
            if user.sale_team_id:
                reseller_id = self.env['res.partner'].sudo().search([('sale_team','=',user.sale_team_id.id)])
                if user.is_master:
                    return super(StockLocation, self).search(args, offset=offset, limit=limit, order=order, count=count)
                if reseller_id:
                    location = reseller_id.resale_location.id
                    args.append(['id','=',location])
        return super(StockLocation, self).search(args, offset=offset, limit=limit, order=order, count=count)

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def action_confirm_user(self):
        return super(StockPicking, self).action_confirm()

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        if 'uid' in self._context:
            user = self.env['res.users'].browse(self._context['uid'])
            if user.sale_team_id:
                reseller_id = self.env['res.partner'].sudo().search([('sale_team','=',user.sale_team_id.id)])
                if user.is_master:
                    return super(StockPicking, self).search(args, offset=offset, limit=limit, order=order, count=count)
                if reseller_id:
                    location = reseller_id.resale_location.id
                    res = ['|',('location_id','=',location),('location_dest_id','=',location)]
                    for j in res:
                        args.append(j)
        return super(StockPicking, self).search(args, offset=offset, limit=limit, order=order, count=count)