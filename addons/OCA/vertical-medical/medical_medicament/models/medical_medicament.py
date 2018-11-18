# -*- coding: utf-8 -*-
# Copyright 2004 Tech-Receptives
# Copyright 2016-2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class MedicalMedicament(models.Model):
    _name = 'medical.medicament'
    _description = 'Medical Medicament'
    _inherit = ['mail.thread']
    _inherits = {'product.product': 'product_id'}

    indications = fields.Text()
    therapeutic_action = fields.Char()
    presentation = fields.Text()
    active_component_ids = fields.Many2many(
        string='Active Ingredients',
        comodel_name='medical.medicament.component',
        compute='_compute_active_ingredient_ids',
    )

    product_id = fields.Many2one(
        comodel_name='product.product',
        required=True,
        ondelete="cascade",
    )
    component_ids = fields.Many2many(
        string='Components',
        comodel_name='medical.medicament.component',
    )
    drug_form_id = fields.Many2one(
        comodel_name='medical.drug.form',
        string='Drug Form',
        required=True,
    )
    drug_route_id = fields.Many2one(
        comodel_name='medical.drug.route',
        string='Drug Route',
    )
    pregnancy_category = fields.Selection(
        selection=[
            ('a', 'A'),
            ('b', 'B'),
            ('c', 'C'),
            ('d', 'D'),
            ('x', 'X'),
            ('n', 'N'),
        ],
        help=(
            '** FDA Pregancy Categories ***\n'
            'CATEGORY A :Adequate and well-controlled human studies have'
            'failed to demonstrate a risk to the fetus in the first'
            'trimester of pregnancy (and there is no evidence of risk in '
            'later trimesters).\n\n'
            'CATEGORY B : Animal reproduction studies have failed to '
            'demonstrate a risk to the fetus and there are no adequate '
            'and well-controlled studies in pregnant women OR Animal '
            'studies have shown an adverse effect, but adequate and '
            'well-controlled studies in pregnant women'
            ' have failed to demonstrate a risk to the fetus in any'
            ' trimester.\n\n'
            'CATEGORY C : Animal reproduction studies have shown an '
            'adverse effect on the fetus and there are no adequate and '
            'well-controlled  studies in humans, but potential benefits '
            'may warrant use of the drug in pregnant women despite '
            'potential risks. \n\n '
            'CATEGORY D : There is positive evidence of human fetal '
            'risk based on adverse reaction data from investigational '
            'or marketing experience or studies in humans, but potential '
            'benefits may warrant use of the drug in pregnant women '
            'despite potential risks.\n\n'
            'CATEGORY X : Studies in animals or humans have demonstrated '
            'fetal abnormalities and/or there is positive evidence of '
            'human fetal risk based on adverse reaction data from '
            'investigational or marketing experience, and the risks '
            'involved in use of the drug in pregnant'
            ' women clearly outweigh potential benefits.\n\n'
            'CATEGORY N : Not yet classified'
        ),
    )
    is_pregnancy_warning = fields.Boolean(
        string='Pregnancy Warning',
        help='The drug represents risk to pregnancy or lactancy',
    )
    dosage_instruction = fields.Text(
        string='Dosage Instructions',
    )
    pregnancy = fields.Text(
        string='Pregnancy Notes',
        help='Description of potential effects to pregnancy',
    )
    notes = fields.Text(
        help='Additional information that may be useful',
    )
    overdosage = fields.Text(
        help='Steps to perform in the event of overdosage',
    )
    adverse_reaction = fields.Text(
        help='Potential adverse reactions',
    )
    strength = fields.Float(
        help='Strength of medicament',
    )
    strength_uom_id = fields.Many2one(
        string='Strength Unit',
        comodel_name='product.uom',
        help='Strength unit of measure',
    )

    @api.multi
    @api.depends('component_ids')
    def _compute_active_ingredient_ids(self):
        for rec in self:
            active = rec.component_ids.filtered(
                lambda r: r.is_active_ingredient
            )
            rec.active_component_ids = [(6, 0, active.ids)]

    @api.multi
    def name_get(self):
        res = []
        for rec in self:
            if rec.drug_form_id.name:
                form = ' - %s' % rec.drug_form_id.code
            else:
                form = ''
            name = '{name} {strength:g} {uom}{form}'.format(
                name=rec.product_id.name,
                strength=rec.strength,
                uom=rec.strength_uom_id.name or '',
                form=form,
            )
            res.append((rec.id, name))
        return res

    @api.multi
    def _onchange_uom(self, uom_id, uom_po_id):
        return self.product_id._onchange_uom(uom_id, uom_po_id)

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        vals['is_medicament'] = True
        return super(MedicalMedicament, self).create(vals)

    @api.model
    @api.returns('self')
    def get_by_product(self, product_id):
        """ Return medicaments associated to a product record """
        return self.search([('product_id', '=', product_id.id)])