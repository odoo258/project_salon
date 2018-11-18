# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2018 - OutTech (<http://www.outtech.com.br>).
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

from odoo import http
from odoo.http import request

class WebsiteController(http.Controller):

    def _prepare_portal_layout_values(self):
        """ prepare the values to render portal layout """
        partner = request.env.user.partner_id
        # get customer sales rep
        if partner.user_id:
            sales_rep = partner.user_id
        else:
            sales_rep = False
        values = {
            'sales_rep': sales_rep,
            'company': request.website.company_id,
            'user': request.env.user
        }
        return values

    @http.route(['/page/laudosonline'], type='http', auth="public", website=True)
    def consultation_page(self, **kwargs):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        exams_ids = request.env['medical.map'].search([('owner_id','=',partner.id),('name','=','lab_test')])

        values.update({
            'exams': exams_ids,
        })

        return http.request.render('hospital_management.medical_exam_consultation', values)

    @http.route(['/page/laudosonline/<int:page>'], type="http", auth="admin", website=True)
    def exams_followup(self, exam=None, **post):
        values = self._prepare_portal_layout_values()
        exam_id = request.env['medical.map'].search([('id', '=', post['page'])])

        values.update({
            'exam': exam_id,
        })
        if exam_id.lab_test_type:
            lab_tst_type_src = request.env['medical.map']._fields['lab_test_type'].selection
            for lab_tst in lab_tst_type_src:
                if lab_tst[0] == exam_id.lab_test_type:
                    lab_tst_str = lab_tst[1]
                    field_translation = request.env['ir.translation'].search([('src', '=', lab_tst[1]),
                                                                              ('lang', '=', request.env.user.lang)])[0].value

                    if field_translation:
                        lab_tst_str = field_translation

                    values.update({
                        'lab_tst_str': lab_tst_str,
                    })

        if exam_id.schedule_state:
            schdl_state_src = request.env['medical.map']._fields['schedule_state'].selection
            for schdl_state in schdl_state_src:
                if schdl_state[0] == exam_id.schedule_state:
                    schdl_state_str = schdl_state[1]
                    field_translation = request.env['ir.translation'].search([('src', '=', schdl_state[1]),
                                                                ('lang', '=', request.env.user.lang)])[0].value

                    if field_translation:
                        schdl_state_str = field_translation
                    values.update({
                        'schdl_state_str': schdl_state_str
                    })

        return http.request.render('hospital_management.exams_followup', values)
