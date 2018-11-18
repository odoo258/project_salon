# coding=utf-8
from odoo import models, fields, api, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    is_hospital = fields.Boolean("Is Hospital")
