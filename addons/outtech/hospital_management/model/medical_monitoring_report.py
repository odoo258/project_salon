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
from odoo.exceptions import ValidationError
from datetime import datetime


class MedicalMonitoringReport(models.Model):
    _name = "medical.monitoring.report"

    @api.model
    def default_get(self, fields):
        res = super(MedicalMonitoringReport, self).default_get(fields)
        # monitoring_obj = self.env['monitoring.type.line']
        monitoring_types = self.env['medical.monitoring.type'].search([('fill_automatic', '=', True)])
        update_vals = []
        if monitoring_types:
            for line in monitoring_types:
                line.write({'included_hour': datetime.now()})
                update_vals.append([0, 0, {'monitoring_type_id': line.id,'register_option': line.register_option, 'included_hour': line.included_hour}])

        res['monitoring_register_ids'] = update_vals
        return res

    @api.model
    def _default_start_date(self):
        date = datetime.now()
        return date

    name = fields.Char('Monitoring Report', copy=False, required=True,
        default=lambda self: self.env['ir.sequence'].next_by_code('medical.monitoring.report'), readonly=True)
    patient_id = fields.Many2one("medical.patient", string=_("Pet"), required=True)
    doctor_id = fields.Many2one('medical.physician', string=_('Veterinary'), required=True)
    start_date = fields.Datetime(string=_("Start Date"), default=_default_start_date)
    diagnostic = fields.Char(string=_("Diagnostic"))
    pet_weight = fields.Integer(string=_("Weight"))
    prognostic = fields.Char(string=_("Prognostic"))
    included_in_admission = fields.Boolean()
    monitoring_register_ids = fields.One2many("monitoring.type.line", "monitoring_report_id", string=_('Register Line'))
    prescription_line_ids = fields.Many2many('medical.prescription.line', string=_('Prescription Line'))


class MonitoringTypeLine(models.Model):
    _name = "monitoring.type.line"

    @api.onchange('register_option')
    def _compute_register(self):
        if self.register_option:
            self.included_hour = datetime.now()
            self.date_invisible = datetime.now()

    monitoring_report_id = fields.Many2one("medical.monitoring.report", string=_("Report"), invisible=True)
    monitoring_type_id = fields.Many2one("medical.monitoring.type", string=_("Name"), invisible=True)
    register_option = fields.Char(string=_("Register"))
    included_hour = fields.Datetime(string=_("Hour"), readonly=True)
    date_invisible = fields.Datetime(invisible=True)

class MonitoringReportLine(models.Model):
    _name = "monitoring.report.line"

    @api.multi
    def unlink(self):
        for line in self.monitoring_report_id:
            line.write({'included_in_admission': False})
        res = super(MonitoringReportLine, self).unlink()
        return res

    def create(self, vals):
        if 'monitoring_report_id' in vals:
            if vals['monitoring_report_id'] == False:
                return False
            src_monitoring = self.env['medical.monitoring.report'].search([('id','=',vals['monitoring_report_id'])])
            src_monitoring.write({'included_in_admission': True})
        vals.update({'start_date': vals['date_invisible']})
        res = super(MonitoringReportLine, self).create(vals)
        return res

    def write(self, vals):
        if 'monitoring_report_id' in vals:
            src_monitoring = self.env['medical.monitoring.report'].search([('id', '=', vals['monitoring_report_id'])])
            src_monitoring.write({'included_in_admission': True})
        res = super(MonitoringReportLine, self).write(vals)
        return res

    @api.onchange('monitoring_report_id')
    def _onchange_monitoring_report(self):
        if self.monitoring_report_id:
            self.monitoring_report_id.included_in_admission = True
            self.date_invisible = datetime.now()
            self.start_date = datetime.now()

    map_id = fields.Many2one("medical.map", string=_("Map"), invisible=True)
    monitoring_report_id = fields.Many2one("medical.monitoring.report", string=_("Report"))
    start_date = fields.Datetime(string=_("Hour"), readonly=True)
    date_invisible = fields.Datetime(invisible=True)

    _sql_constraints = [
        ('monitoring_report_uniq', 'unique(monitoring_report_id)', _("There is already another map with this monitoring report"))]
