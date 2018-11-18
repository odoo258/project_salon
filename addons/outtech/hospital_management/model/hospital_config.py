# coding=utf-8
# Author: Christian Douglas <christian.douglas.alcantara@gmail.com>
from odoo import fields, models, api


class HospitalConfigSettings(models.Model):
    _name = 'hospital.config.settings'
    _inherit = 'res.config.settings'

    time_alert = fields.Integer(
        string="Time Alert", help="Minutes", default_model='hospital.config.settings'
    )
    users = fields.Many2many(
        'res.users', string="Users", help="Users to alert", default_model='hospital.config.settings'
    )

    def get_default_time_alert(self, fields):
        time_alert = int(self.env['ir.config_parameter'].get_param('time_alert', default=0))
        return dict(time_alert=time_alert)

    def get_default_users(self, fields):
        users = self.env['ir.config_parameter'].get_param('users', default='[]')
        return dict(users=eval(users))

    def set_default_users(self):
        self.env['ir.config_parameter'].set_param('users', self.users.ids)

    def set_default_time_alert(self):
        self.env['ir.config_parameter'].set_param('time_alert', self.time_alert)