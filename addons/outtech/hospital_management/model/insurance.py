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
from datetime import datetime, timedelta
from odoo import api, fields, models, _


class InsuranceCompany(models.Model):
    _inherit = "res.partner"

    is_person = fields.Boolean('Person')
    is_doctor = fields.Boolean('Doctor')
    is_institution = fields.Boolean('Institution')
    is_insurance_company = fields.Boolean('Insurance Company')
    insurance_ids = fields.One2many('medical.insurance', 'insurance_compnay_id', 'Insurance')
    ref = fields.Char('ID Number')
    contact_method = fields.Selection(
        string="Contact Method", selection=[
            ('email', _('Email')),
            ('tel', _('Phone')),
            ('sms', _('SMS')),
            ('whatsapp', _('Whatsapp')),
            ('other', _('Other'))
        ]
    )
    contact_method_obs = fields.Text(
        string="Contact Method Observation"
    )
    how_did_find = fields.Selection(
        string="How did you find us?", selection=[
            ("from_friend", _("From a friend")),
            ("search_engine", _("Search engine")),
            ("tv_radio", _("TV or radio")),
            ("nwespaper_magazine", _("Newspaper or magazine ad")),
            ("bussines_associate", _("Business associate")),
            ("internet_ad", _("Internet ad")),
            ("link_page", _("Link from another page")),
            ("other", _("Other"))
        ]
    )
    how_did_find_obs = fields.Text(
        string="Observation"
    )

    @api.multi
    def update_register(self):
        sql = """update res_partner set write_date = '%s' where id = %s""" % (datetime.today(),self.id)
        self.env.cr.execute(sql)
        return {
            'warning': {
                'title': _("Warning"),
                'message': _("Update Customer Ready!")
            }
        }

    @api.model
    def receivable_move_line(self):
        """
        Retorna as parcelas vencidas do cliente.
        """
        rml = self.env['account.move.line']
        date_now = fields.Date.today()
        args = [
            ('partner_id', '=', self.id),
            ('full_reconcile_id', '=', False),
            ('account_id.internal_type', '=', 'receivable'),
            ('account_id.reconcile', '=', True),
            ('date_maturity', '<=', date_now)
        ]
        res = rml.search(args)
        print('>>>>', len(res), res)
        return res



class Insurance(models.Model):
    _name = 'medical.insurance'
    _rec_name = 'insurance_compnay_id'

    number = fields.Char('Number')
    name = fields.Many2one('res.partner', 'Owner')
    patient_id = fields.Many2one('res.partner', 'Owner')
    type = fields.Selection([('state', 'State'), ('private', 'Private'), ('labour_union', 'Labour Union/ Syndical')],
                            'Insurance Type')
    member_since = fields.Date('Member Since')
    insurance_compnay_id = fields.Many2one('res.partner', 'Insurance Compnay')
    category = fields.Char('Category')
    notes = fields.Text('Extra Info')
    member_exp = fields.Date('Expiration Date')
    plan_id = fields.Many2one('medical.insurance.plan', 'Plan')


class InsurancePlan(models.Model):
    _name = 'medical.insurance.plan'
    _rec_name = 'plan_id'

    plan_id = fields.Many2one('product.product', 'Plan', domain="[('type','=','service')]")
    is_default = fields.Boolean('Default Plan')
    company_id = fields.Many2one('res.partner', 'Company')
    notes = fields.Text('Extra Info')


    # vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
