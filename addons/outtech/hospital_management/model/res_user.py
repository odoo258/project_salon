# coding=utf-8
# Author: Christian Douglas <christian.douglas.alcantara@gmail.com>
from odoo import models, fields


class ResUser(models.Model):
    _inherit = 'res.users'

    is_hospital_manager = fields.Boolean()
