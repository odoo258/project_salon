# coding=utf-8
# Author: Christian Douglas <christian.douglas.alcantara@gmail.com>
from odoo import models, fields, api, _


class AdmissionReactivateWizard(models.TransientModel):
    _name = 'admission.reactivate.wizard'
    REASONS = [
        ('op1', _('Option 01')),
        ('op2', _('Option 02')),
        ('op3', _('Option 03')),
        ('op4', _('Option 04')),
        ('other', _('Other'))
    ]
    reason = fields.Selection(
        string="Reason for Reactivation", selection=REASONS, required=True
    )
    observation = fields.Text(
        string="Observation", required=True
    )

    @api.one
    def btn_reactivate(self):
        active_id = self._context.get('active_id')
        vals = {
            'name': self.reason,
            'observation': self.observation,
            'admission_id': active_id
        }
        self.env['admission.reactivate.log'].create(vals)
        admission = self.env['medical.inpatient.registration'].browse(active_id)
        admission.state = 'open'
        return {'type': 'ir.actions.act_window_close'}
