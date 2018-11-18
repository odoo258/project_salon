# coding=utf-8
# Author: Christian Douglas <christian.douglas.alcantara@gmail.com>
from odoo import models, fields, _
from . medical_map import MedicalMap

class Product(models.Model):
    _inherit = 'product.template'

    medical_type = fields.Selection(
        string="Medical Type", selection=MedicalMap.TYPE
    )
    sur_material_ids = fields.One2many('medical.product', 'product_id', string="Materials")


class MedicalProduct(models.Model):
    _name = 'medical.product'

    product_id = fields.Many2one('product.product', string="Product")
    quantity = fields.Integer(string="Quantity", required=True)


class VaccinesLine(models.Model):
    _name = 'vaccines.line'

    map_id = fields.Many2one("medical.map", string=_("Map"))
    vaccine_id = fields.Many2one("product.template", string=_("Vaccine"), domain=[('medical_type', '=', 'vaccines')])
    application_date = fields.Date(string=_("Application Date"))
    dose = fields.Char(string=_("Dose"))
    next_application_date = fields.Date(string=_("Next Application Date"))