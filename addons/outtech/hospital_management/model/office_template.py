# coding=utf-8
# Author: Christian Douglas <christian.douglas.alcantara@gmail.com>
from odoo import models, fields, api
from .medical_map import MedicalMap


class MedicalOfficeTemplate(models.Model):
    _name = 'medical.office.template'

    name = fields.Char(
        string="Name", required=True
    )
    type = fields.Selection(
        string="Type", selection=MedicalMap.TYPE
    )
    mail_template_id = fields.Many2one(
        'mail.template', string="Template", required=True
    )


class TemplateReport(models.AbstractModel):
    _name = 'report.hospital_management.report_template_officep'
    @api.multi
    def render_html(self, docids, data=None):
        report_obj = self.env['report']
        active_ids = self.env.context.get('active_ids', [])
        maps = self.env['medical.map'].browse(active_ids)
        docargs = {
            'doc_ids': active_ids,
            'doc_model': 'medical.map',
            'docs': maps,
            'user': self.env.user,
            'res_company': self.env.user.company_id,
            'data': {'content': 'okokokok'}
        }
        print '>>>>', docargs, data
        return report_obj.render('hospital_management.report_template_office', docargs)