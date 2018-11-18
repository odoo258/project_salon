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
#domain=[('resale', '=', True)]
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields, api, _

class ResCompany(models.Model):
    _inherit = 'res.company'

    url_api = fields.Char('URL-API', required=True)
    active_api = fields.Boolean('Active-API')
    type_transition = fields.Selection([('AuthOnly','AuthOnly'),('AuthAndCapture','AuthAndCapture')], 'Transition Type')
    url_api_googlemaps = fields.Char('Url GoogleMaps', default='http://maps.googleapis.com/maps/api/distancematrix/json?origins=@origin&destinations=@dest&mode=driving&language=pt-BR&sensor=false', help='EX: http://maps.googleapis.com/maps/api/distancematrix/json?origins=@origin&destinations=@dest&mode=driving&language=pt-BR&sensor=false')
    radius_search = fields.Integer('Radius in Meters', default=5000, help='EX: 5000 refernce a (5 km)')