# coding=utf-8
# Author: Christian Douglas <christian.douglas.alcantara@gmail.com>
from odoo import models, fields, api, _
from odoo.exceptions import Warning


class UnlockClienteWizard(models.TransientModel):
    _name = 'unlock.client.wizard'

    def _get_default(self):
        owner_id = self._context.get('owner_id')
        res = []
        if owner_id:
            owner = self.env['res.partner'].browse(owner_id)
            res = map(lambda x: x.id, owner.receivable_move_line())
        return res

    def _get_users(self):
        group_manager = self.env.ref('sales_team.group_sale_manager')
        res = map(lambda x: (x.id, x.name), group_manager.users)
        return res

    owner_id = fields.Many2one(
        'res.partner', string='Owner', readonly=True
    )
    move_line_ids = fields.Many2many(
        'account.move.line', string="Account Move Line", default=_get_default, # , default=_get_service_ids, readonly=True
    )
    user = fields.Selection(
        string="User", selection=_get_users, required=True
    )
    password = fields.Char(
        string="Password", required=True
    )

    @api.model
    def default_get(self, fields):
        res = super(UnlockClienteWizard, self).default_get(fields)
        owner_id = self._context.get('owner_id')
        if owner_id:
            res['owner_id'] = owner_id
        return res

    @api.multi
    def action_unlock(self):
        user = self.env['res.users'].browse(int(self.user))
        user.check_credentials(self.password)
        mi = self.env['medical.appointment'].browse(self._context['active_id'])
        mi.locked = False
        mi.unlocked = True
        msg = _(u"Client <strong>{}</strong> unlocked by <strong>{}</strong>".format(self.owner_id.name, user.name))
        mi.message_post(body=msg)
