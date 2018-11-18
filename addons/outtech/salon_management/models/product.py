# coding=utf-8
# Author: Christian Douglas <christian.douglas.alcantara@gmail.com>

from odoo import models, fields


class Product(models.Model):
    _inherit = 'product.template'

    time_taken = fields.Float(
        string='Time Taken', default=0
    )
