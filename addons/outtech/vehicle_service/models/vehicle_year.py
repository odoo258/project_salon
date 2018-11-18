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

from odoo import models, fields, api

class VehicleYear(models.Model):
    _name = 'vehicle.year'
    _order = 'name desc'

    name = fields.Char(string='Vehicle Year', required=True)

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):

        if 'model_id' in self._context:
            if self._context['model_id']:
                br_vehicle_model = self.env['vehicle.model'].browse(self._context['model_id'])
                args.insert(0, ('id', 'in', br_vehicle_model.year_ids.ids))
            else:
                args.insert(0, ('id', '=', 0))

        return super(VehicleYear, self)._search(args, offset=offset, limit=limit, order=order,
                                                count=False, access_rights_uid=access_rights_uid)