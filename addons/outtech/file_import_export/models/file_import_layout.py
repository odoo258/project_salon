# -*- encoding: utf-8 -*-
##############################################################################
#
#    OutTech - Brasil
#    Copyright (C) OutTech Services IT (<http://www.outtech.com.br>).
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
from odoo.exceptions import UserError

class FileImportLayout(models.Model):
    _name = 'file.import.layout'

    # TXT

    def txt_import_file(self, data):

        obj_line_import = self.env['file.import.layout.line']

        dict_data = {'header':[], 'detail':[], 'footer':[]}

        cont = 0

        dict_detail_lines = {}
        dict_field_header = {}
        dict_field_detail = {}
        dict_field_footer = {}

        while data:

            id_line = data[0]

            if data[0] in ('\n','\r'):
                data = data[1:]
                continue

            src_line = obj_line_import.search([('field_identifier', '=', True),('fixed_value', '=', id_line)])

            if not src_line:
                raise UserError(_('Error! The register type was not found!'))

            if src_line.file_import_layout_header_id:
                type = 'header'
                br_line = src_line.file_import_layout_header_id

            elif src_line.file_import_layout_detail_id:
                dict_detail_lines = {}
                type = 'detail'
                br_line = src_line.file_import_layout_detail_id

            elif src_line.file_import_layout_footer_id:
                type = 'footer'
                br_line = src_line.file_import_layout_footer_id

            for field in br_line.file_import_layout_line_ids:

                length_field = field.length

                if type == 'header':
                    dict_field_header.update({field.code: data[:length_field]})

                elif type == 'detail':
                    dict_detail_lines.update({field.code: data[:length_field]})

                elif type == 'footer':
                    dict_field_footer.update({field.code: data[:length_field]})

                # if field.break_line:
                #     length_field += 1

                data = data[length_field:]

            if type == 'detail':
                dict_field_detail[cont] = dict_detail_lines
                cont += 1

        dict_data['header'].append(dict_field_header)

        dict_data['detail'].append(dict_field_detail)

        dict_data['footer'].append(dict_field_footer)

        return dict_data

    # CSV


    # XML


    #Divisor Method
    def import_file(self, layout_name, data):

        src_layout = self.search([('code', '=', layout_name)])

        if not src_layout:
            raise UserError(_('Error! The import layout was not found!'))

        if src_layout.file_import_type == 'csv':
            return self.csv_import_file(data)

        elif src_layout.file_import_type == 'txt':
            return self.txt_import_file(data)

        elif src_layout.file_import_type == 'xml':
            return self.xml_import_file(data)

        else:
            raise UserError(_('Error! Extension file not avaliable! Use Only XML, CSV and TXT'))



    name = fields.Char('Name', required=True)
    code = fields.Char('Code', required=True)
    active = fields.Boolean('Active', default=True)
    file_import_type = fields.Selection([('csv', 'CSV'), ('txt', 'TXT'), ('xml', 'XML')], 'Type of Import File',  required=True)
    record_separator = fields.Char('Record Separator')
    description = fields.Text('Description')
    file_import_layout_header_ids = fields.One2many('file.import.layout.header', 'file_import_layout_id', 'Header')
    file_import_layout_detail_ids = fields.One2many('file.import.layout.detail', 'file_import_layout_id', 'Detail')
    file_import_layout_footer_ids = fields.One2many('file.import.layout.footer', 'file_import_layout_id', 'Footer')


class FileImportLayoutHeader(models.Model):
    _name = 'file.import.layout.header'
    _order = 'sequence'

    name = fields.Char('Name', required=True)
    active = fields.Boolean('Active', default=True)
    sequence = fields.Integer('Sequence', required=True)
    file_import_layout_id = fields.Many2one('file.import.layout', 'File Import Layout', ondelete='cascade')
    file_import_layout_line_ids = fields.One2many('file.import.layout.line', 'file_import_layout_header_id', 'File Import Layout Lines')

class FileImportLayoutDetail(models.Model):
    _name = 'file.import.layout.detail'
    _order = 'sequence'

    name = fields.Char('Name', required=True)
    active = fields.Boolean('Active', default=True)
    sequence = fields.Integer('Sequence', required=True)
    file_import_layout_id = fields.Many2one('file.import.layout', 'File Import Layout', ondelete='cascade')
    file_import_layout_line_ids = fields.One2many('file.import.layout.line', 'file_import_layout_detail_id', 'File Import Layout Lines')



class FileImportLayoutFooter(models.Model):
    _name = 'file.import.layout.footer'
    _order = 'sequence'

    name = fields.Char('Name', required=True)
    active = fields.Boolean('Active', default=True)
    sequence = fields.Integer('Sequence', required=True)
    file_import_layout_id = fields.Many2one('file.import.layout', 'File Import Layout', ondelete='cascade')
    file_import_layout_line_ids = fields.One2many('file.import.layout.line', 'file_import_layout_footer_id', string='File Import Layout Lines')



class FileImportLayoutLine(models.Model):
    _name = 'file.import.layout.line'
    _order = 'sequence'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', required=True)
    active = fields.Boolean(string='Active', default=True)
    sequence = fields.Integer(string='Sequence', required=True)
    parent_id = fields.Many2one('file.import.layout.line', string='Parent')
    field_identifier = fields.Boolean(string='Field Identifier', default=False)
    fixed_value = fields.Char(string='Fixed Value')
    # data_type = fields.Selection([('character', 'Character'), ('float', 'Float'), ('date', 'Date')], string='Data Type')
    length = fields.Integer(string='Length')
    # decimal_separator = fields.Char(string='Decimal Separator')
    # decimal_precision = fields.Integer(string='Decimal Precision')
    # left_padding = fields.Char(string='Left Padding')
    # right_padding = fields.Char(string='Right Padding')
    # prefix = fields.Char(string='Prefix')
    # suffix = fields.Char(string='Suffix')
    # letter_case = fields.Selection([('lower_case', 'Lower Case'), ('upper_case', 'Upper Case')], string='Letter Case')
    # accent_marks = fields.Boolean(string='Accent Marks')
    break_line = fields.Boolean(string='Break Line')
    # hide_if_empty = fields.Boolean(string='Hide If Empty')
    # special_character = fields.Boolean(string='Special Character')
    # date_format = fields.Selection([('dd-mm-yyyy', 'dd-mm-yyyy'), ('dd-mm-yy', 'dd-mm-yy'),
    #                                 ('mm-dd-yyyy', 'mm-dd-yyyy'), ('mm-dd-yy', 'mm-dd-yy'),
    #                                 ('yyyy-mm-dd', 'yyyy-mm-dd'), ('yy-mm-dd', 'yy-mm-dd'),
    #                                 ('yyyy-dd-mm', 'yyyy-dd-mm'), ('yy-dd-mm', 'yy-dd-mm'), ], string='Date Format')
    # csv_separator = fields.Char(string='CSV Separator')
    # xml_tag = fields.Char(string='XML Tag')
    # xml_field_type = fields.Selection([('declaration', 'Declaration'), ('tag', 'Tag'), ('section_cdata', 'Section CDATA')], string='XML Field Type')
    # xml_attributes_ids = fields.One2many('file.export.xml.attributes', 'file_export_layout_line_id', string='XML Attributes')
    file_import_layout_header_id = fields.Many2one('file.import.layout.header', string='File Import Layout Header', ondelete='cascade')
    file_import_layout_detail_id = fields.Many2one('file.import.layout.detail', string='File Import Layout Detail', ondelete='cascade')
    file_import_layout_footer_id = fields.Many2one('file.import.layout.footer', string='File Import Layout Footer', ondelete='cascade')