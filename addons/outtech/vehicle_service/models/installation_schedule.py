# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2017 - OutTech (<http://www.outtech.com.br>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields, api, _
from datetime import date, timedelta, datetime
from odoo.exceptions import UserError
import logging
import pytz
import requests as req
from dateutil import relativedelta
from datetime import date
import requests
import json
_logger = logging.getLogger(__name__)

class InstallationSchedule(models.Model):
    _name = 'installation.schedule'

    def _get_protocol(self):
        return self.env['ir.sequence'].next_by_code('installation.schedule') or 'New'

    name = fields.Char(string='Name', required=True, default=_get_protocol, readonly=True)
    name_aux = fields.Char(string='Name Aux')
    date_scheduler = fields.Date(string='Date Scheduler')
    period = fields.Selection([('morning','Morning'),('afternoon','Afternoon'),('night','Night')], string='Period')
    reseller_id = fields.Many2one('res.partner',string='Reseller', domain=[('resale', '=', True)])
    equipment_id = fields.Many2one('stock.production.lot',string='Equipment', readonly=True)
    equipment_draft_id = fields.Many2one('stock.production.lot',string='Equipment', readonly=True)
    partner_id = fields.Many2one('res.partner',string='Partner', required=True)
    type_id = fields.Many2one('installation.schedule.type',string='Type', required=True)
    sale_order_id = fields.Many2one('sale.order',string='Sale Order')
    contract_id = fields.Many2one('sale.subscription',string='Contract')
    observation = fields.Text(string='Observation')
    state = fields.Selection([('draft','Draft'),('confirmed','Confirmed'),('activated','Activated'),('remove_equipment','Equipamento Retirado'),('canceled','Canceled')], default='draft', string='State')
    date_start = fields.Datetime(string='Date Start')
    date_end = fields.Datetime(string='Date End')
    option_vehicle = fields.Boolean(string='Option Vehicle')
    vehicle_id = fields.Many2one('vehicle.partner', string='Vehicle', domain="[('partner_id', '=', partner_id)]")
    plate = fields.Char(string='Plate', related='vehicle_id.plate', readonly=True)
    manufacturer_id = fields.Many2one('vehicle.manufacturer', related='vehicle_id.manufacturer_id', string='Manufacturer', readonly=True)
    model_id = fields.Many2one('vehicle.model', related='vehicle_id.model_id', string='Model', readonly=True)
    year_id = fields.Many2one('vehicle.year', related='vehicle_id.year_id', string='Year', readonly=True)

    #Busca Revenda
    type_search = fields.Selection([('zip','CEP'),('city','Cidade')],'Tipo de Busca')
    zip = fields.Char('CEP')
    state_id = fields.Many2one("res.country.state", string='Estado', domain="[('country_id', '=', 32)]")
    city_id = fields.Many2one('res.state.city', u'Município', domain="[('state_id','=',state_id)]")


    @api.model
    def create(self, vals):

        type = self.env['installation.schedule.type'].browse(vals['type_id']).type

        if type == 'withdrawal':
            installations = self.search([('partner_id', '=', vals['partner_id']), ('type_id.type', '=', 'inst'), ('state', '=', 'activated'), ('vehicle_id', '=', vals['vehicle_id'])])
            if installations and len(installations) == 1:
                vals.update({'equipment_id': installations.equipment_id.id,
                             'sale_order_id': installations.sale_order_id.id,
                             'contract_id': installations.contract_id.id})
        if 'name_aux' in vals:
            vals.update({'name': vals['name_aux']})
        return super(InstallationSchedule, self).create(vals)

    @api.multi
    def remove_equipament_button(self):
        if self.equipment_id:
            company = self.env['res.company'].browse(1)
            headers = {"Content-Type": "application/json", "Accept": "application/json"}
            if not self.equipment_id.id_plataforma:
                raise UserError(_(u'Equipamento não possui ID vinculado!'))
            url = company.url_api + '/api/plans/sell/cancel/' + self.equipment_id.id_plataforma
            response = requests.post(url, data={}, headers=headers)
            if response.status_code in [200,201]:
                self.sudo().write({'state':'remove_equipment'})
                return {'warning':{'title': _('Aviso!'), 'message': _('Equipamento Retirado com Sucesso!')}}
            else:
                return {'warning':{'title': _('Aviso!'), 'message': _('Erro no processo de retirado!')}}
        return {'warning':{'title': _('Aviso!'), 'message': _('Nenhum Equipamento Encontrado!')}}

    @api.onchange('name')
    def name_change(self):
        return {'value': {'name_aux': self.name}}


    @api.onchange('type_search')
    def type_search_address(self):
        res = {}
        if self.type_search == 'zip':
            res = {'state_id':False, 'city_id':False}
        if self.type_search == 'city':
            res = {'zip':''}
        if not self.type_search:
            res = {'state_id':False, 'city_id':False,'zip':''}
        return {'value':res}

    @api.onchange('zip','city_id')
    def zip_city_search(self):
        user = self.env['res.users'].browse(self._uid)
        url = user.company_id.url_api_googlemaps
        radius = user.company_id.radius_search
        res = []
        if self.zip:
            cont = 0
            origin = self.zip
            destination = ''
            for d in self.env['res.partner'].search([('resale','=',True)]):
                if d.zip:
                    destination = destination + d.zip + '|'
            url_search = url.replace('@origin',origin).replace('@dest',destination)
            try:
                google_search = req.get(url_search)
            except:
                return {'domain':{'reseller_id':[('id','in',res)]},'warning':{'title': _('Aviso!'), 'message': _(u'Erro de Conexão')}}
            result = google_search.json()
            cont_result = len(result['destination_addresses'])
            dest_list = destination.split('|')
            while cont < cont_result:
                if result['rows'][0]['elements'][cont]['status'] == 'OK' and \
                                result['rows'][0]['elements'][cont]['distance']['value'] < radius:
                    resales = self.env['res.partner'].search([('resale','=',True),('zip','=',dest_list[cont])]).id
                    res.append(resales)
                cont += 1
            if not res:
                return {'domain':{'reseller_id':[('id','in',res)]},'warning':{'title': _('Aviso!'), 'message': _('Nenhum Revenda Encontrado!')}}
            domain = {'reseller_id':[('id','in',res)]}
        elif self.city_id:
            resales = self.env['res.partner'].search([('resale','=',True),('city_id','=',self.city_id.id)])
            res = [i.id for i in resales]
            if not res:
                return {'domain':{'reseller_id':[('id','in',res)]},'warning':{'title': _('Aviso!'), 'message': _('Nenhum Revenda Encontrado!')}}
            domain = {'reseller_id':[('id','in',res)]}

        else:
            return False
        return {'domain':domain}

    @api.onchange('vehicle_id')
    def vehicle_change(self):
        if self.vehicle_id:
            installations = self.search([('partner_id','=',self.partner_id.id),('type_id.type','=', 'inst'),('state','=','activated'),('vehicle_id','=',self.vehicle_id.id)])
            if installations and len(installations) == 1:
                return {'value':{'equipment_id':installations.equipment_id.id,
                                 'sale_order_id': installations.sale_order_id.id,
                                 'contract_id': installations.contract_id.id}}
            else:
                return {'warning': {'title': _('WARNING'), 'message': _('Verify Equipment to vehicle!')},'value':{'equipment':False}}
        return {}

    @api.onchange('partner_id')
    def partner_change(self):
        return {'value':{'type_id':False, 'option_vehicle':False, 'vehicle_id':False}}

    @api.onchange('type_id')
    def type_change(self):
        if not self.vehicle_id and self.type_id:
            if not self.partner_id:
                raise UserError(_('Please select first customer!'))
            vehicles = self.search([('partner_id','=',self.partner_id.id),('type_id.type','=','inst'),('state','=','activated')])
            if vehicles:
                if len(vehicles) > 1:
                    return {'warning': {'title': _('WARNING'), 'message': _('Select Vehicle!')},'value':{'option_vehicle':True}}
                else:
                    return {'value':{'vehicle_id':vehicles.vehicle_id.id, 'option_vehicle':False}}
        return {}

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        if 'uid' in self._context:
            user = self.env['res.users'].browse(self._context['uid'])
            resale_manager = self.env['crm.team'].search([('user_id','=',user.id)])
            if self._uid == 1:
                return super(InstallationSchedule, self).search(args, offset=offset, limit=limit, order=order, count=count)
            if user.is_master:
                return super(InstallationSchedule, self).search(args, offset=offset, limit=limit, order=order, count=count)
            if user.sale_team_id:
                resale = self.env['res.partner'].search([('sale_team','=',user.sale_team_id.id)])
                args.append('|')
                args.append(('reseller_id','=',resale.id))
                args.append(('reseller_id','=',False))
            if resale_manager:
                resale = self.env['res.partner'].search([('sale_team','=',resale_manager.id)])
                args.append('|')
                args.append(('reseller_id','=',resale.id))
                args.append(('reseller_id','=',False))
        return super(InstallationSchedule, self).search(args, offset=offset, limit=limit, order=order, count=count)


    @api.onchange('period')
    def period_change(self):
        if self.period:
            if not self.reseller_id or not self.date_scheduler:
                return {'warning': {'title': _('WARNING'), 'message': _('Please check Resale and date!')},'value':{'period':''}}
            qty_disp = self.reseller_id.qty_installers * 2
            qty = self.env['installation.schedule'].sudo().search([('reseller_id','=',self.reseller_id.id),
                                                      ('date_scheduler','=',self.date_scheduler),
                                                      ('period','=',self.period),
                                                      ('state','=','confirmed')])
            if len(qty) >= qty_disp:
                return {'warning': {'title': _('WARNING'), 'message': _('Period not available')},'value':{'period':''}}
        return {}

    @api.onchange('date_scheduler')
    def date_schedule_change(self):
        return {'value':{'period':''}}

    @api.onchange('reseller_id')
    def reseller_id_change(self):
        return {'value':{'period':'','date_scheduler':''}}

    @api.onchange('period', 'date_scheduler')
    def period_date_scheduler_change(self):

        larger_date = []
        if not 'tz' in self._context:
            {'warning': {'title': _('WARNING'), 'message': _('Insert Time Zone in User')},'value':{'date_scheduler':''}}
        for date_timezone in pytz.timezone(self._context.get('tz'))._utc_transition_times:
            if date_timezone > datetime.now():
                larger_date.append(date_timezone)

        timezone = min(larger_date)

        if self.period and self.date_scheduler:
            if self.period == 'morning':
                vals = {
                    'date_start': self.date_scheduler + ' ' + '%02d' % (6 + timezone.hour) +':00:00',
                    'date_end': self.date_scheduler + ' ' + '%02d' % (12 + timezone.hour) +':00:00',
                }
            elif self.period == 'afternoon':
                vals = {
                    'date_start': self.date_scheduler + ' ' + '%02d' % (12 + timezone.hour) +':00:00',
                    'date_end': self.date_scheduler + ' ' + '%02d' % (18 + timezone.hour) +':00:00',
                }
            elif self.period == 'night':
                vals = {
                    'date_start': self.date_scheduler + ' ' + '%02d' % (18 + timezone.hour) +':00:00',
                    'date_end': str(datetime.strptime(self.date_scheduler, "%Y-%m-%d") + timedelta(days=1)),
                }

            return {'value': vals}

        return {'value': {'date_start': '', 'date_end': ''}}

    @api.multi
    def confirm_button(self):
        return self.write({'state': 'confirmed'})

    @api.multi
    def schedule_button(self):

        if not self.date_scheduler:
            raise UserError(_('Date Scheduler not found! This field is required!'))

        if not self.period:
            raise UserError(_('Period not found! This field is required!'))

        if not self.reseller_id:
            raise UserError(_('Reseller not found! This field is required!'))

        self.write({'state': 'confirmed'})

        br_quick_sale = self.sale_order_id.quick_sale_id

        br_quick_sale.write({'state': 'scheduled'})
        # TODO Cria um template de email para envio
        template_id = self.env['mail.template'].search([('model', '=', 'quick.sale'),('domain', '=', 'installation')]) # TODO incluir novo parametro para busca



        if not template_id:
            raise UserError(_('There is no email template for sale confirmation'))

        mail_values = template_id.generate_email(br_quick_sale.id)

        vals_email = {
            'subject': mail_values['subject'],
            'email_from': mail_values['email_from'],
            'email_to': mail_values['email_to'],
            'body_html': mail_values['body_html'],
            'auto_delete': False,
            'state': 'outgoing',
            'model': mail_values['model'],
            'res_id': mail_values['res_id'],
        }

        self.env['mail.mail'].create(vals_email)

        return {'type': 'ir.actions.act_window_close'}

    # @api.multi
    # def activate_button(self):
    #
    #     dummy, view_id = self.env['ir.model.data'].get_object_reference('vehicle_service','search_serial_number_form')
    #
    #     return {
    #         'name': "Activate",
    #         'view_mode': 'form',
    #         'view_id': view_id,
    #         'view_type': 'form',
    #         'res_model': 'search.serial.number',
    #         'type': 'ir.actions.act_window',
    #         'nodestroy': True,
    #         'target': 'new',
    #         'domain': '[]',
    #         'context': {}
    #     }
        # return self.write({'state': 'activated'})

    @api.multi
    def return_draft_button(self):

        br_quick_sale = self.sale_order_id.quick_sale_id

        br_quick_sale.write({'state': 'paid'})

        return self.write({'state': 'draft'})

    @api.multi
    def cancel_button(self):
        return self.write({'state': 'canceled'})

    @api.multi
    def activate_button(self):
        if self.type_id.type not in ['inst','change']:
            raise UserError(_(u"Agendameto não permite ativação!"))
        dummy, view_id = self.env['ir.model.data'].get_object_reference('vehicle_service', 'view_activate_contract_dialog_form')

        return {
            'name':_("Activate"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'installation.active',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
                'close_after_process': True
            }
        }

class InstallationActive(models.TransientModel):
    _name = 'installation.active'

    serial_number = fields.Char(string="Serial Number")

    def process_active(self):
        if 'active_id' in self._context:
            headers = {"Content-Type": "application/json", "Accept": "application/json"}
            inst = self.env['installation.schedule'].browse(self._context['active_id'])
            args = {'msg':'', 'contract_id':''}
            if not inst.equipment_draft_id:
                args['msg'] = 'Sem Equipamento Cadastrado!'
                raise UserError(_("Sem Equipamento Cadastrado!"))
            else:
                if not inst.equipment_draft_id.id_plataforma:
                    args['msg'] = u'Equipamento ainda não Ativo na Plataforma!'
                    raise UserError(_(u'Equipamento ainda não Ativo na Plataforma!'))
            company = self.env['res.company'].browse(1)
            url = company.url_api + '/api/trackings?by=device&device=%s&limit=1' % inst.equipment_draft_id.id_plataforma
            info = req.get(url, headers=headers)
            if info.status_code in [200,201]:
                res_info = json.loads(info.text)
                if 'content' in res_info and res_info['content']:
                    content = res_info['content'][0]
                    sensors = content['sensors']
                    sensor_valid = False
                    if sensors:
                        for s in sensors:
                            if s['type'] == 'ACC_OFF':
                                if s['value'] == 'ON':
                                    sensor_valid = True
                                else:
                                    sensor_valid = False
                    else:
                        sensor_valid = False
                    if not content['valid'] or not content['latitude'] or not content['longitude'] or not sensor_valid:
                        raise UserError(_(u'Não é possível ativar contrato sem finalizar os testes de Equipamentos!'))
                else:
                    raise UserError(_(u'Não é possível ativar contrato sem finalizar os testes de Equipamentos!'))
            if inst.sale_order_id:
                picking_type = False
                picking = self.env['stock.picking'].search([('state','!=','done'),('sale_id','=',inst.sale_order_id.id),('location_dest_id','=',9)])
                if not picking:
                    type = self.env['stock.picking.type'].search([('default_location_src_id','=',inst.reseller_id.resale_location.id),
                                                                     ('code','=','outgoing')])
                    if not type:
                        raise UserError(_("Sem tipo de movimentacao de estoque pre definada na configuracao!"))
                    dict_p = {

                        'partner_id': inst.partner_id.id,
                        'location_id': inst.reseller_id.resale_location.id,
                        'location_dest_id': 9,
                        'picking_type_id': type[0].id
                    }
                    picking = self.env['stock.picking'].create(dict_p)

                    dict_line_p = {

                        'name': inst.name,
                        'origin': inst.name,
                        'product_id': inst.equipment_draft_id.product_id.id,
                        'product_uom': inst.equipment_draft_id.product_id.uom_id.id,
                        'product_uom_qty': 1,
                        'location_id': inst.reseller_id.resale_location.id,
                        'location_dest_id': 9,
                        'restrict_lot_id': inst.equipment_draft_id.id,
                        'picking_id': picking.id

                    }
                    self.env['stock.move'].create(dict_line_p)
                if picking and inst.reseller_id:

                    picking.action_confirm()
                    picking.do_transfer()
                else:
                    args['msg'] = 'Sem Revendedor Cadastrado!'
                    raise UserError(_("Sem Revendedor Cadastrado!"))
            if inst.sudo().contract_id:
                if inst.sudo().contract_id.state != 'draft':
                    args['msg'] = 'Contrato ja Ativo!'
                    raise UserError(_("Contrato ja Ativo!"))
                else:
                    date_new = date.today() + relativedelta.relativedelta(days=30)
                    self.env['sale.subscription'].sudo().browse(inst.sudo().contract_id.id).set_open()
                    self.env['sale.subscription'].sudo().browse(inst.sudo().contract_id.id).write({'recurring_next_date': date_new})
                    args.update({'contract_id':inst.sudo().contract_id.id})
                    inst.sudo().write({'equipment_id':inst.sudo().equipment_draft_id.id,'state':'activated'})
                    quick_sale = self.env['quick.sale'].sudo().search([('installation_id','=',inst.sudo().id)])
                    if quick_sale:
                        quick_sale.sudo().write({'state':'done'})
                return req.post('http://localhost/api/contract/active.php', args)
            else:
                args['msg'] = 'Sem contrato definido!'
                raise UserError(_("Sem Contrato Cadastrado!"))
                #return req.post('http://localhost/api/contract/active.php', args)
        return True

class InstallationWebSite(models.Model):
    _name = 'installation.website'

    date_scheduler = fields.Date(string='Date Scheduler', required=True)
    period = fields.Selection([('morning','Morning'),('afternoon','Afternoon'),('night','Night')], string='Period', required=True)
    reseller_id = fields.Many2one('res.partner',string='Reseller', domain=[('resale', '=', True)], required=True)

    @api.model
    def create(self, vals):
        res = super(InstallationWebSite, self).create(vals)
        partner_id = self.env['res.users'].browse(self._context['uid']).partner_id.id
        inst = self.env['installation.schedule'].search([('partner_id','=',partner_id),('state','=','draft')])
        if inst:
            values = vals
            values.update({'state':'confirmed'})
            inst[0].write(values)
        #    return request.redirect("/")
        else:
            raise UserError(_('Error in Create'))
        return res


class InstallationScheduleType(models.Model):
    _name = 'installation.schedule.type'

    name = fields.Char(u'Name', required=True)
    type = fields.Selection([('inst','Installation'),('mro','Maintenance'),('withdrawal','Withdrawal'),('change','Change Vehicle')], u'Type', required=True)

    _sql_constraints = [('uniq_name', 'unique(type)', _("The type must be unique !"))]