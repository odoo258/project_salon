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
import logging
import re

_logger = logging.getLogger(__name__)

class FileExportLayout(models.Model):
    _name = 'file.export.layout'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', required=True)
    active = fields.Boolean(string='Active', default=True)
    description = fields.Text(string='Description')
    file_export_type = fields.Selection([('csv','CSV'),('txt','TXT'),('xml','XML')], string='Type of Export File', required=True)
    txt_type = fields.Selection([('hdf','HDF'),('hldlf','HLDLF')], string='Type TXT File', default='hdf')
    file_export_layout_header_ids = fields.One2many('file.export.layout.header', 'file_export_layout_id', string='Header')
    file_export_layout_lot_header_ids = fields.One2many('file.export.layout.lot.header', 'file_export_layout_id', string='Lot of Header')
    file_export_layout_detail_ids = fields.One2many('file.export.layout.detail', 'file_export_layout_id', string='Detail')
    file_export_layout_lot_footer_ids = fields.One2many('file.export.layout.lot.footer', 'file_export_layout_id', string='Lot of Footer')
    file_export_layout_footer_ids = fields.One2many('file.export.layout.footer', 'file_export_layout_id', string='Footer')

    @api.multi
    def create_file(self, layout, data):

        file_export_layout_id = self.search([('code', '=', layout), ('active', '=', True)])

        if not file_export_layout_id:
            raise UserError(_('Error! Layout not found!'))

        if len(file_export_layout_id) > 1:
            raise UserError(_('Error! Have more one layout registered with the same name!'))

        obj_file_export_layout_line = self.env['file.export.layout.line']

        header = {}
        lot_header = {}
        detail = {}
        lot_footer = {}
        footer = {}

        for line_header in file_export_layout_id.file_export_layout_header_ids:

            if line_header.condition:
                if line_header.condition in data['header'] and not data['header'][line_header.condition]:
                    continue

            items_line_header = []

            br_file_export_layout_line = obj_file_export_layout_line.search([('file_export_layout_header_id', '=', line_header.id), ('active', '=', True)], order='sequence')

            for item_header in br_file_export_layout_line:

                items_line_header.append(item_header)

            header.update({str(line_header.name): items_line_header})

        for record_data in data['lot_header']:

            lot_header.update({record_data:{}})

            for line_lot_header in file_export_layout_id.file_export_layout_lot_header_ids:

                if line_lot_header.condition:
                    if line_lot_header.condition in data['lot_header'][record_data] and not data['lot_header'][record_data][line_lot_header.condition]:
                        continue

                items_line_lot_header = []

                br_file_export_layout_line = obj_file_export_layout_line.search([('file_export_layout_lot_header_id', '=', line_lot_header.id), ('active', '=', True)], order='sequence')

                for item_lot_header in br_file_export_layout_line:

                    items_line_lot_header.append(item_lot_header)

                lot_header[record_data] = items_line_lot_header

        for record_data in data['detail']:

            detail.update({record_data:{}})

            for line_detail in file_export_layout_id.file_export_layout_detail_ids:

                if line_detail.condition:
                    if line_detail.condition in data['detail'][record_data] and not data['detail'][record_data][line_detail.condition]:
                        continue

                items_line_detail = []

                br_file_export_layout_line = obj_file_export_layout_line.search([('file_export_layout_detail_id', '=', line_detail.id), ('active', '=', True)], order='sequence')

                for item_detail in br_file_export_layout_line:

                    items_line_detail.append(item_detail)

                detail[record_data] = items_line_detail

        for record_data in data['lot_footer']:

            lot_footer.update({record_data:{}})

            for line_lot_footer in file_export_layout_id.file_export_layout_lot_footer_ids:

                if line_lot_footer.condition:
                    if line_lot_footer.condition in data['lot_footer'][record_data] and not data['lot_footer'][record_data][line_lot_footer.condition]:
                        continue

                items_line_lot_footer = []

                br_file_export_layout_line = obj_file_export_layout_line.search([('file_export_layout_lot_footer_id', '=', line_lot_footer.id), ('active', '=', True)], order='sequence')

                for item_lot_footer in br_file_export_layout_line:

                    items_line_lot_footer.append(item_lot_footer)

                lot_footer[record_data] = items_line_lot_footer

        for line_footer in file_export_layout_id.file_export_layout_footer_ids:

            if line_footer.condition:
                if line_footer.condition in data['footer'] and not data['footer'][line_footer.condition]:
                    continue

            items_line_footer = []

            br_file_export_layout_line = obj_file_export_layout_line.search([('file_export_layout_footer_id', '=', line_footer.id), ('active', '=', True)], order='sequence')

            for item_footer in br_file_export_layout_line:

                items_line_footer.append(item_footer)

            footer.update({str(line_footer.name): items_line_footer})

        items_file = {'header': header, 'lot_header': lot_header, 'detail': detail, 'lot_footer': lot_footer, 'footer': footer}

        if file_export_layout_id.file_export_type == 'csv':
            return self.csv_create_file

        elif file_export_layout_id.file_export_type == 'txt':

            if file_export_layout_id.txt_type == 'hdf':
                return self.txt_hdf_create_file(data, items_file)

            elif file_export_layout_id.txt_type == 'hldlf':
                return self.txt_hldlf_create_file(data, items_file)

        elif file_export_layout_id.file_export_type == 'xml':
            return self.xml_create_file(data, items_file)

        else:
            raise UserError(_('Error! Extension file not avaliable! Use Only XML, CSV and TXT'))

    # TXT HDF
    def txt_hdf_create_file(self, data, items_file):

        txt = ''

        obj_file_export_layout_line = self.env['file.export.layout.line']

        list_header = sorted(items_file['header'].items(), key=lambda x: x[0])

        for line_header in list_header:

            for field_header in line_header[1]:

                if field_header.fixed_value:

                    txt += '%s' % (obj_file_export_layout_line.get_formated(field_header.fixed_value, field_header))

                elif field_header.code in data['header']:

                    txt += '%s' % (obj_file_export_layout_line.get_formated(data['header'][field_header.code], field_header))

                else:

                    txt += '%s' % (obj_file_export_layout_line.get_formated('', field_header))

            txt += '\r\n'

        lines_detail = sorted(items_file['detail'].items(), key=lambda x: x[0])

        for record in lines_detail:

            for line_detail in record[1]:

                for field_detail in record[1][line_detail]:

                    if field_detail.fixed_value:
                        txt += '%s' % (obj_file_export_layout_line.get_formated(field_detail.fixed_value, field_detail))

                    elif field_detail.code in data['detail'][record[0]]:
                        txt += '%s' % (obj_file_export_layout_line.get_formated(data['detail'][record[0]][field_detail.code], field_detail))

                    else:
                        if field_detail.hide_if_empty:
                            continue
                        else:
                            txt += '%s' % (obj_file_export_layout_line.get_formated('', field_detail))

                txt += '\r\n'

        list_footer = sorted(items_file['footer'].items(), key=lambda x: x[0])

        for line_footer in list_footer:

            for field_footer in line_footer[1]:

                if field_footer.fixed_value:

                    txt += '%s' % (obj_file_export_layout_line.get_formated(field_footer.fixed_value, field_footer))

                elif field_footer.code in data['footer']:

                    txt += '%s' % (obj_file_export_layout_line.get_formated(data['footer'][field_footer.code], field_footer))

                else:

                    txt += '%s' % (obj_file_export_layout_line.get_formated('', field_footer))

        return txt

    # TXT HLDLF
    def txt_hldlf_create_file(self, data, items_file):

        txt = ''

        obj_file_export_layout_line = self.env['file.export.layout.line']

        list_header = sorted(items_file['header'].items(), key=lambda x: x[0])

        for line_header in list_header:

            for field_header in line_header[1]:

                if field_header.fixed_value:

                    txt += '%s' % (obj_file_export_layout_line.get_formated(field_header.fixed_value, field_header))

                elif field_header.code in data['header']:

                    txt += '%s' % (obj_file_export_layout_line.get_formated(data['header'][field_header.code], field_header))

                else:

                    txt += '%s' % (obj_file_export_layout_line.get_formated('', field_header))

            txt += '\r\n'

        list_lot_header = sorted(items_file['lot_header'].items(), key=lambda x: x[0])

        for record_lot_header in list_lot_header:

            for field_lot_header in record_lot_header[1]:

                if field_lot_header.fixed_value:
                    txt += '%s' % (obj_file_export_layout_line.get_formated(field_lot_header.fixed_value, field_lot_header))

                elif field_lot_header.code in data['lot_header'][record_lot_header[0]]:
                    txt += '%s' % (obj_file_export_layout_line.get_formated(data['lot_header'][record_lot_header[0]][field_lot_header.code], field_lot_header))

                else:

                    if field_lot_header.hide_if_empty:
                        continue

                    else:
                        txt += '%s' % (obj_file_export_layout_line.get_formated('', field_lot_header))

            txt += '\r\n'

            lines_detail = sorted(items_file['detail'].items(), key=lambda x: x[0])

            for detail in lines_detail:

                detail_number = detail[0].rsplit('/', 1)[0]

                if not detail_number == str(record_lot_header[0]):
                    continue

                for field_detail in detail[1]:

                    if field_detail.fixed_value:
                        txt += '%s' % (obj_file_export_layout_line.get_formated(field_detail.fixed_value, field_detail))

                    elif field_detail.code in data['detail'][detail[0]]:
                        txt += '%s' % (obj_file_export_layout_line.get_formated(data['detail'][detail[0]][field_detail.code],field_detail))
                    else:
                        if field_detail.hide_if_empty:
                            continue
                        else:
                            txt += '%s' % (obj_file_export_layout_line.get_formated('', field_detail))
                txt += '\r\n'

            lines_lot_footer = sorted(items_file['lot_footer'].items(), key=lambda x: x[0])

            for lot_footer in lines_lot_footer:

                if not lot_footer[0] == record_lot_header[0]:
                    continue

                for field_lot_footer in lot_footer[1]:

                    if field_lot_footer.fixed_value:
                        txt += '%s' % (obj_file_export_layout_line.get_formated(field_lot_footer.fixed_value, field_lot_footer))

                    elif field_lot_footer.code in data['lot_footer'][lot_footer[0]]:
                        txt += '%s' % (obj_file_export_layout_line.get_formated(data['lot_footer'][lot_footer[0]][field_lot_footer.code], field_lot_footer))
                    else:
                        if field_lot_footer.hide_if_empty:
                            continue
                        else:
                            txt += '%s' % (obj_file_export_layout_line.get_formated('', field_lot_footer))
                txt += '\r\n'

        list_footer = sorted(items_file['footer'].items(), key=lambda x: x[0])

        for line_footer in list_footer:

            for field_footer in line_footer[1]:

                if field_footer.fixed_value:

                    txt += '%s' % (obj_file_export_layout_line.get_formated(field_footer.fixed_value, field_footer))

                elif field_footer.code in data['footer']:

                    txt += '%s' % (obj_file_export_layout_line.get_formated(data['footer'][field_footer.code], field_footer))

                else:

                    txt += '%s' % (obj_file_export_layout_line.get_formated('', field_footer))

        return txt

class FileExportLayoutHeader(models.Model):
    _name = 'file.export.layout.header'
    _order = 'sequence'

    name = fields.Char(string='Name', required=True)
    active = fields.Boolean(string='Active', default=True)
    sequence = fields.Integer(string='Sequence', required=True)
    condition = fields.Char(string='Condition')
    file_export_layout_id = fields.Many2one('file.export.layout', string='File Export Layout', ondelete='cascade')
    file_export_layout_line_ids = fields.One2many('file.export.layout.line', 'file_export_layout_header_id', string='File Export Layout Lines')

class FileExportLayoutLotHeader(models.Model):
    _name = 'file.export.layout.lot.header'
    _order = 'sequence'

    name = fields.Char(string='Name', required=True)
    active = fields.Boolean(string='Active', default=True)
    sequence = fields.Integer(string='Sequence', required=True)
    condition = fields.Char(string='Condition')
    file_export_layout_id = fields.Many2one('file.export.layout', string='File Export Layout', ondelete='cascade')
    file_export_layout_line_ids = fields.One2many('file.export.layout.line', 'file_export_layout_lot_header_id', string='File Export Layout Lines')


class FileExportLayoutDetail(models.Model):
    _name = 'file.export.layout.detail'
    _order = 'sequence'

    name = fields.Char(string='Name', required=True)
    active = fields.Boolean(string='Active', default=True)
    sequence = fields.Integer(string='Sequence', required=True)
    condition = fields.Char(string='Condition')
    file_export_layout_id = fields.Many2one('file.export.layout', string='File Export Layout', ondelete='cascade')
    file_export_layout_line_ids = fields.One2many('file.export.layout.line', 'file_export_layout_detail_id', string='File Export Layout Lines')


class FileExportLayoutLotFooter(models.Model):
    _name = 'file.export.layout.lot.footer'
    _order = 'sequence'

    name = fields.Char(string='Name', required=True)
    active = fields.Boolean(string='Active', default=True)
    sequence = fields.Integer(string='Sequence', required=True)
    condition = fields.Char(string='Condition')
    file_export_layout_id = fields.Many2one('file.export.layout', string='File Export Layout', ondelete='cascade')
    file_export_layout_line_ids = fields.One2many('file.export.layout.line', 'file_export_layout_lot_footer_id', string='File Export Layout Lines')


class FileExportLayoutFooter(models.Model):
    _name = 'file.export.layout.footer'
    _order = 'sequence'

    name = fields.Char(string='Name', required=True)
    active = fields.Boolean(string='Active', default=True)
    sequence = fields.Integer(string='Sequence', required=True)
    condition = fields.Char(string='Condition')
    file_export_layout_id = fields.Many2one('file.export.layout', string='File Export Layout', ondelete='cascade')
    file_export_layout_line_ids = fields.One2many('file.export.layout.line', 'file_export_layout_footer_id', string='File Export Layout Lines')

class FileExportLayoutLine(models.Model):
    _name = 'file.export.layout.line'
    _order = 'sequence'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', required=True)
    active = fields.Boolean(string='Active', default=True)
    sequence = fields.Integer(string='Sequence', required=True)
    parent_id = fields.Many2one('file.export.layout.line', string='Parent')
    fixed_value = fields.Char(string='Fixed Value')
    data_type = fields.Selection([('character','Character'),('date','Date'),('float','Float'),('integer','Integer')], string='Data Type')
    length = fields.Integer(string='Length')
    decimal_separator = fields.Char(string='Decimal Separator')
    decimal_precision = fields.Integer(string='Decimal Precision')
    left_padding = fields.Char(string='Left Padding')
    right_padding = fields.Char(string='Right Padding')
    prefix = fields.Char(string='Prefix')
    suffix = fields.Char(string='Suffix')
    letter_case = fields.Selection([('lower_case','Lower Case'),('upper_case','Upper Case')], string='Letter Case')
    accent_marks = fields.Boolean(string='Accent Marks')
    break_line = fields.Boolean(string='Break Line')
    hide_if_empty = fields.Boolean(string='Hide If Empty')
    special_character = fields.Boolean(string='Special Character')
    date_format = fields.Selection([('dd-mm-yyyy','dd-mm-yyyy'),('dd-mm-yy','dd-mm-yy'),
                                    ('mm-dd-yyyy','mm-dd-yyyy'),('mm-dd-yy','mm-dd-yy'),
                                    ('yyyy-mm-dd','yyyy-mm-dd'),('yy-mm-dd','yy-mm-dd'),
                                    ('yyyy-dd-mm','yyyy-dd-mm'),('yy-dd-mm','yy-dd-mm'),], string='Date Format')
    csv_separator = fields.Char(string='CSV Separator')
    xml_tag = fields.Char(string='XML Tag')
    xml_field_type = fields.Selection([('declaration','Declaration'),('tag','Tag'),('section_cdata','Section CDATA')], string='XML Field Type')
    # xml_attributes_ids = fields.One2many('file.export.xml.attributes', 'file_export_layout_line_id', string='XML Attributes')
    file_export_layout_header_id = fields.Many2one('file.export.layout.header', string='File Export Layout Header', ondelete='cascade')
    file_export_layout_lot_header_id = fields.Many2one('file.export.layout.lot.header', string='File Export Layout Lot of Header', ondelete='cascade')
    file_export_layout_detail_id = fields.Many2one('file.export.layout.detail', string='File Export Layout Detail', ondelete='cascade')
    file_export_layout_lot_footer_id = fields.Many2one('file.export.layout.lot.footer', string='File Export Layout Lot of Footer', ondelete='cascade')
    file_export_layout_footer_id = fields.Many2one('file.export.layout.footer', string='File Export Layout Footer', ondelete='cascade')

    @api.multi
    @api.onchange("data_type")
    def _onchange_data_type(self):
        if self.data_type:
            if self.data_type == 'character':
                self.right_padding = ' '
            elif self.data_type == 'integer':
                self.left_padding = 0

    def get_formated(self, value, field):

        if field.data_type == 'float':
            if value:

                value = float(value)

            if field.decimal_precision:

                mask_dp = '%.' + '%s' % (field.decimal_precision) + 'f'
                value = mask_dp % (round(value, field.decimal_precision))

            if field.decimal_separator:
                value = re.sub('[^0-9]', field.decimal_separator, str(value))

        if field.data_type == 'character':

            value = unicode(value)

            if field.letter_case == 'lower_case':
                value = value.lower()

            elif field.letter_case == 'upper_case':
                value = value.upper()

            if not field.accent_marks:
                value = self._spe_char_remove(value)

        elif field.data_type == 'date':

            if value:
                if field.date_format:
                    if field.date_format == 'dd-mm-yyyy':
                        value = '%02d%02d%04d' % (value.day, value.month, value.year)
                    elif field.date_format == 'dd-mm-yy':
                        value = '%02d%02d%s' % (value.day, value.month, str(value.year)[2:])
                    elif field.date_format == 'mm-dd-yyyy':
                        value = '%02d%02d%04d' % (value.month, value.day, value.year)
                    elif field.date_format == 'mm-dd-yy':
                        value = '%02d%02d%s' % (value.month, value.day, str(value.year)[2:])
                    elif field.date_format == 'yyyy-dd-mm':
                        value = '%04d%02d%02d' % (value.year, value.day, value.month)
                    elif field.date_format == 'yy-dd-mm':
                        value = '%s%02d%02d' % (str(value.year)[2:], value.day, value.month)
                    elif field.date_format == 'yy-mm-dd':
                        value = '%s%02d%02d' % (str(value.year)[2:], value.month, value.day)

        if not field.special_character:

            value = re.sub('[^A-Za-z0-9\s+]', '', str(value))

        if field.length:
            value = value[:field.length]

            if field.left_padding:
                value = unicode(value)
                value = value.rjust(field.length, unicode(field.left_padding))

            elif field.right_padding:
                value = unicode(value)
                value = value.ljust(field.length, unicode(field.right_padding))

        if field.prefix:
            value = '%s%s' %(field.prefix, value)

        if field.suffix:
            value = '%s%s' %(value, field.suffix)

        if field.break_line:
            value = '%s\r\n' %(value)

        return value

    def _spe_char_remove(self, text):

        if text == None or text == False:
            return text == ''

        text = (text).encode('utf-8')

        dic = {'á':'a', 'à':'a', 'â':'a', 'ã':'a', 'Á':'A', 'À':'A', 'Â':'A', 'Ã':'A',
               'é':'e', 'è':'e', 'ê':'e', 'ẽ':'e', 'É':'E', 'È':'E', 'Ê':'E', 'Ẽ':'E',
               'í':'i', 'ì':'i', 'î':'i', 'ĩ':'i', 'Í':'I', 'Ì':'I', 'Î':'I', 'Ĩ':'I',
               'ó':'o', 'ò':'o', 'ô':'o', 'õ':'o', 'Ó':'O', 'Ò':'O', 'Ô':'O', 'Õ':'O',
               'ú':'u', 'ù':'u', 'û':'u', 'ũ':'u', 'Ú':'U', 'Ù':'U', 'Û':'U', 'Ũ':'U',
               'ç':'c', 'Ç':'C'}

        for s, r in dic.iteritems():
            text = text.replace(s, r)

        return re.sub('[^a-zA-Z0-9/&. -]', '', text)


