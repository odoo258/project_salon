# -*- coding: utf-8 -*-
##############################################################################
#
#    This module uses OpenERP, Open Source Management Solution Framework.
#    Copyright (C) 2014-Today BrowseInfo (<http://www.browseinfo.in>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################
import pytz
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_TIME_FORMAT
from datetime import datetime



class SalonPromotionGroup(models.Model):
    _name = "salon.promotiongroup"

    name = fields.Char(string='Description', required=True )

    info = fields.Text('Extra Info')

    service_ids = fields.One2many(
        'salon.promotiongroup.services', inverse_name='promotiongroup_id', string=_("Services Included")
    )


    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        return super(SalonPromotionGroup, self).name_search(name=name, args=args, operator=operator, limit=100)


class SalonPromotionGroupServices(models.Model):
    _name = 'salon.promotiongroup.services'
    _rec_name = 'promotiongroup_id'

    services = fields.Many2one(
        'product.template', string="Services", domain=[('type', '=', 'service')], required=True
    )
    promotiongroup_id = fields.Many2one(
        'salon.promotiongroup', string=_("Promotion Group")
    )
