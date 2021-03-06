# -*- encoding: utf-8 -*-
###############################################################################
#                                                                             #
# Copyright (C) 2015 Trustcode - www.trustcode.com.br                         #
#              Danimar Ribeiro <danimaribeiro@gmail.com>                      #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU Affero General Public License as published by #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################

import cPickle
from decimal import Decimal
from odoo import api, fields, models
from odoo.tools.translate import _
from odoo.exceptions import Warning
import re
from datetime import date


class NfeImportEdit(models.Model):
    _name = 'nfe.import.edit'

    # returns true if the barcode is a valid EAN barcode
    @api.multi
    def check_ean(self, ean):
       return re.match("^\d+$", ean) and self.ean_checksum(ean) == int(ean[-1])

    def ean_checksum(self, ean):
        code = list(ean)
        if len(code) != 13:
            return -1

        oddsum = evensum = total = 0
        code = code[:-1] # Remove checksum
        for i in range(len(code)):
            if i % 2 == 0:
                evensum += int(code[i])
            else:
                oddsum += int(code[i])
        total = oddsum * 3 + evensum
        return int((10 - total % 10) % 10)

    @api.multi
    def name_get(self):
        return [(rec.id,
                 u"Editando NF-e ({0})".format(
                     rec.number)) for rec in self]

    @api.multi
    def _default_category(self):
        return self.env['ir.model.data'].get_object_reference(
            'product', 'product_category_all')[1]

    def _default_company(self):
        return self.env.user.company_id

    company_id = fields.Many2one('res.company', string="Empresa",
                                 default=_default_company)
    currency_id = fields.Many2one(related='company_id.currency_id',
                                  string='Moeda', readonly=True)
    xml_data = fields.Char(string="Xml Data", size=200000, readonly=True)
    edoc_input = fields.Binary(u'Arquivo do documento eletrônico',
                               help=u'Somente arquivos no formato TXT e XML')
    file_name = fields.Char('File Name', size=128)

    number = fields.Char(string="Número", size=20, readonly=True)
    supplier_id = fields.Many2one('res.partner', string="Fornecedor",
                                  readonly=True)

    natureza_operacao = fields.Char(string="Natureza da operação", size=200,
                                    readonly=True)
    amount_total = fields.Float(string="Valor Total", digits=(18, 2),
                                readonly=True)

    import_from_invoice = fields.Boolean(u'Importar da fatura')
    account_invoice_id = fields.Many2one('account.invoice',
                                         u'Fatura de compra',
                                         readonly=True)
    fiscal_position = fields.Many2one(
        'account.fiscal.position', 'Posição Fiscal')

    warehouse_id = fields.Many2one('stock.warehouse','Warehouse', required=True, domain="[('company_id','=', company_id)]")

    journal_id = fields.Many2one('account.journal','Journal', required=True, domain="[('type','=','purchase')]")

    product_import_ids = fields.One2many('nfe.import.products',
                                         'nfe_import_id', string="Produtos")
    create_product = fields.Boolean(
        u'Criar produtos automaticamente?', default=True,
        help=u'Cria o produto automaticamente caso não seja informado um')

    product_category_id = fields.Many2one('product.category',
                                          u'Categoria Produto',
                                          default=_default_category)

    state = fields.Selection([('draft','Draft'),('confirmed','Confirmed'),('cancel','Cancel')],u'State', default='draft')

    date = fields.Date('Imported Date')

    date_confirmed = fields.Date('Confirmed Date')

    @api.model
    def create(self, values):
        return super(NfeImportEdit, self).create(values)

    @api.multi
    def cancel(self):
        return self.write({'state':'cancel'})

    def _validate(self):
        indice = 0
        for item in self.product_import_ids:
            if self.import_from_invoice and not item.invoice_line_id:
                raise Warning(
                    u'Escolha a linha da fatura correspondente: {0} - {1}'
                    .format(str(indice), item.product_xml))
            if self.import_from_invoice and \
                    item.invoice_line_id.product_id.id != item.product_id.id:
                raise Warning(
                    u'Produto incompatível com a linha da fatura: {0} - {1}'
                    .format(str(indice), item.product_xml))
            if self.import_from_invoice and \
                    '%.2f' % item.invoice_line_id.price_unit != '%.2f' % item.unit_amount_xml:
                raise Warning(
                    u'Valor do produto unitario incompativeis: %s\n\
                    Valor Unitario xml: %s - Valor Unitario Fatura: %s'
                    % (item.product_xml, '%.2f' % item.unit_amount_xml, '%.2f' % item.invoice_line_id.price_unit))
            if self.import_from_invoice and \
                    item.quantity_xml != item.invoice_line_id.quantity:
                raise Warning(
                    u'Quantidades do produto incompativeis: %s\n\
                    Quantidade xml: %s - Quantidade Fatura: %s'
                    % (item.product_xml,item.quantity_xml, item.invoice_line_id.quantity))
            if not item.product_id:
                raise Warning(u'Escolha o produto do item {0} - {1}'.format(
                              str(indice), item.product_xml))
            if not item.cfop_id:
                raise Warning(u'Escolha a CFOP do item {0} - {1'.format(
                              str(indice), item.product_xml))

            if not item.uom_id:
                raise Warning(u'Escolha a Unidade do item {0} - {1}'.format(
                              str(indice), item.product_xml))

            if item.product_id.uom_po_id.category_id.id !=\
                    item.uom_id.category_id.id:

                raise Warning(u'Unidades de medida incompatíveis no item \
                            {0} - {1}'.format(str(indice), item.product_xml))
            indice += 1

    @api.multi
    def confirm_values(self):
        self.ensure_one()
        inv_values = cPickle.loads(self.xml_data.encode('ascii', 'ignore'))

        index = 0
        for item in self.product_import_ids:
            line = inv_values['invoice_line'][index]

            if not item.product_id:
                if self.create_product:

                    product_created = self.product_create(
                        inv_values, line, item, self.product_category_id)
                    item.product_id = product_created
                    item.uom_id = product_created.uom_id

                    line[2]['product_id'] = product_created.id
                    line[2]['uos_id'] = product_created.uom_id.id
                    line[2]['account_id'] = product_created.property_account_income_id.id or product_created.categ_id.property_account_income_categ_id.id

                    self.env['product.supplierinfo'].create({
                        'name': self.supplier_id.id,
                        'product_name': item.product_xml,
                        'product_code': item.code_product_xml,
                        'product_tmpl_id': item.product_id.product_tmpl_id.id
                    })

            else:
                line[2]['product_id'] = item.product_id.id
                line[2]['account_id'] = item.product_id.property_account_income_id.id or item.product_id.categ_id.property_account_income_categ_id.id
                line[2]['uos_id'] = item.uom_id.id
                line[2]['cfop_id'] = item.cfop_id.id
                line[2]['fiscal_position_id'] = self.fiscal_position.id

                total_recs = self.env['product.supplierinfo'].search_count(
                    [('name', '=', self.supplier_id.id),
                     ('product_code', '=', item.code_product_xml)]
                )
                if total_recs == 0:
                    self.env['product.supplierinfo'].create({
                        'name': self.supplier_id.id,
                        'product_name': item.product_xml,
                        'product_code': item.code_product_xml,
                        'product_tmpl_id': item.product_id.product_tmpl_id.id
                    })

            inv_values['invoice_line'][index] = line

            index += 1

        self._validate()
        inv_values['journal_id'] = self.journal_id.id

        invoice = self.save_invoice_values(inv_values)
        if not self.account_invoice_id:
            self.create_stock_picking(invoice)
        self.attach_doc_to_invoice(invoice.id, self.edoc_input,
                                   self.file_name)

        imd = self.env['ir.model.data']
        action = imd.xmlid_to_object('account.action_invoice_tree1')
        list_view_id = imd.xmlid_to_res_id('account.invoice_tree')
        form_view_id = imd.xmlid_to_res_id('account.invoice_supplier_form')
        self.write({'account_invoice_id':invoice.id,'state':'confirmed','date_confirmed':date.today()})
        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'views': [[list_view_id, 'tree'], [form_view_id, 'form'], [False, 'graph'], [False, 'kanban'], [False, 'calendar'], [False, 'pivot']],
            'target': action.target,
            'context': action.context,
            'res_model': action.res_model,
        }
        result['domain'] = "[('id','in',[%s])]" % invoice.id

        return result

    @api.multi
    def save_invoice_values(self, inv_values):
        self.ensure_one()
        #error = True
        if self.account_invoice_id:
            vals = {
                'vendor_serie': inv_values['vendor_serie'],
                'fiscal_document_id': inv_values['fiscal_document_id'],
                'date_hour_invoice': inv_values['date_hour_invoice'],
                'date_in_out': inv_values['date_in_out'],
                'number': inv_values['vendor_number'],
                'comment': inv_values['comment'],
                'fiscal_comment': inv_values['fiscal_comment'],
                'nfe_access_key': inv_values['nfe_access_key'],
                'nfe_version': inv_values['nfe_version'],
                'nfe_purpose': inv_values['nfe_purpose'],
#                'freight_responsibility': inv_values['freight_responsibility'],
#                'carrier_name': inv_values['carrier_name'],
#                'vehicle_plate': inv_values['vehicle_plate'],
                'total_frete': inv_values['total_frete'],
                'total_seguro': inv_values['total_seguro'],
                #'amount_costs': inv_values['amount_costs'],
                'fiscal_document_related_ids': inv_values['fiscal_document_related_ids']
            }


            index = 0
            for item in self.product_import_ids:
                if 'invoice_line' in inv_values:
                    line_xml = inv_values['invoice_line'][index]
                else:
                    line_xml = inv_values['invoice_line_ids'][index][2]
                vals = {
                    'cfop_id': item.invoice_line_id.cfop_id.id or item.cfop_id.id,
                    'invoice_id': self.account_invoice_id.id,
                }
                # if item.invoice_line_id.price_unit != item.unit_amount_xml:
                #     item.write({'error':'Valor Devergente!'})
                #     error = True
                #     continue
                # else:
                #     line_xml[2].update(vals)
                #     item.invoice_line_id.write(line_xml[2])
                #     index += 1

            #if not error:
            self.account_invoice_id.write(vals)
            # else:
            #     return {'warning': {'title': _('WARNING'), 'message': _('Divergencia')}}


            #self.account_invoice_id.button_reset_taxes()

            return self.account_invoice_id
        else:
            inv_values['invoice_line_ids'] = inv_values['invoice_line']
            del inv_values['invoice_line']
            #journal_id = self.env['account.journal'].search([('company_id', '=', inv_values['company_id']),
                                                             #('type','=','purchase')])
            if not inv_values['journal_id']:
                raise Warning(u'Journal not defined!')
                #inv_values['journal_id'] = journal_id.id
            inv_values['issuer'] = '0'
            inv_values['number'] = inv_values['vendor_number']
            inv_values['fiscal_document_id'] = False
            invoice = self.env['account.invoice'].create(inv_values)
            # invoice.button_reset_taxes()

            return invoice

    @api.multi
    def product_create(
            self, inv_values, line, item_grid, default_category=None):
        if not line[2]['fiscal_classification_id']:
            fc_env = self.env['product.fiscal.classification']
            ncm = fc_env.search([('name', '=', line[2]['ncm_xml'])], limit=1)
            if not ncm:
                ncm = fc_env.create({
                    'name': line[2]['ncm_xml'],
                    'company_id': inv_values['company_id'],
                    'type': 'normal'
                })
            line[2]['fiscal_classification_id'] = ncm.id

        vals = {
            'name': line[2]['product_name_xml'],
            'type': 'product',
            'fiscal_type': 'product',
            'ncm_id': line[2]['fiscal_classification_id'],
            'default_code': line[2]['product_code_xml'],
        }

        if default_category:
            vals['categ_id'] = default_category.id

        if self.check_ean(line[2]['ean_xml']):
            vals['ean13'] = line[2]['ean_xml']

        if item_grid.uom_id:
            vals['uom_id'] = item_grid.uom_id.id
            vals['uom_po_id'] = item_grid.uom_id.id

        product_tmpl = self.env['product.template'].create(vals)
        return product_tmpl.product_variant_ids[0]

    def create_stock_picking(self, invoice):
        # warehouse = self.env['stock.warehouse'].search([
        #     ('company_id', '=', self.env.user.company_id.id)
        # ])
        # picking_type_id = self.env['stock.picking.type'].search([
        #     ('warehouse_id', '=', warehouse.id), ('code', '=', 'incoming')
        # ])
        # Alterando para pegar o cadastro escolhido na importação
        warehouse = self.warehouse_id
        picking_type_id = warehouse.in_type_id

        if not picking_type_id:
            raise Warning(u'Nenhum de movimentação definida para esse Ármazem')

        picking_vals = {
            'name': '/',
            'origin': 'Fatura: %s-%s' % (invoice.internal_number,
                                         invoice.vendor_serie),
            'partner_id': invoice.partner_id.id,
            'invoice_state': 'none',
            'fiscal_position': invoice.fiscal_position_id.id,
            'picking_type_id': picking_type_id.id,
            'location_id': picking_type_id.default_location_src_id.id,
            'location_dest_id': picking_type_id.default_location_dest_id.id,
            'move_lines': [],
        }
        for line in invoice.invoice_line_ids:
            move_vals = {
                'name': line.product_id.name,
                'product_id': line.product_id.id,
                'product_uom_qty': line.quantity,
                'product_uom': line.product_id.uom_po_id.id,
                'invoice_state': 'none',
                'fiscal_position': invoice.fiscal_position_id.id,
                'location_id': picking_type_id.default_location_src_id.id,
                'location_dest_id': picking_type_id.default_location_dest_id.id,
            }
            picking_vals['move_lines'].append((0, 0, move_vals))

        picking = self.env['stock.picking'].create(picking_vals)
        picking.action_confirm()

    @api.onchange('fiscal_position_id')
    def position_fiscal_onchange(self):
        for item in self.product_import_ids:
            item.cfop_id = self.fiscal_position_id.cfop_id.id

    def attach_doc_to_invoice(self, invoice_id, doc, file_name):
        obj_attachment = self.env['ir.attachment']

        attachment_id = obj_attachment.create({
            'name': file_name,
            'datas': doc,
            'description': _('Xml de entrada NF-e'),
            'res_model': 'account.invoice',
            'res_id': invoice_id
        })
        return attachment_id


class NfeImportProducts(models.Model):
    _name = 'nfe.import.products'

    nfe_import_id = fields.Many2one('nfe.import.edit', string="Nfe Import")
    invoice_id = fields.Many2one('account.invoice', related='nfe_import_id.account_invoice_id')

    invoice_line_id = fields.Many2one(
        'account.invoice.line', string='Linha da fatura',
        domain="[('invoice_id', '=', invoice_id)]")
    product_id = fields.Many2one('product.product', string="Produto")
    uom_id = fields.Many2one('product.uom', string="Unidade de Medida")
    cfop_id = fields.Many2one('br_account.cfop', string="CFOP")

    code_product_xml = fields.Char(
        string="Código Forn.", size=20, readonly=True)
    product_xml = fields.Char(string="Produto Forn.", size=120, readonly=True)
    uom_xml = fields.Char(string="Un. Medida Forn.", size=10, readonly=True)
    cfop_xml = fields.Char(string="CFOP Forn.", size=10, readonly=True)
    error = fields.Char(string="Divergencia", readonly=True)

    quantity_xml = fields.Float(
        string="Quantidade", digits=(18, 4), readonly=True)
    unit_amount_xml = fields.Float(
        string="Valor Unitário", digits=(18, 4), readonly=True)
    discount_total_xml = fields.Float(
        string="Desconto total", digits=(18, 2), readonly=True)
    total_amount_xml = fields.Float(
        string="Valor Total", digits=(18, 2), readonly=True)

    @api.onchange('invoice_line_id')
    def invoice_line_id_onchange(self):
        if self.invoice_line_id:
            if self.invoice_line_id.quantity != self.quantity_xml:
                return {'value': {'invoice_line_id': False, },
                        'warning': {
                    'title': u'Atenção',
                    'message': u'Quantidades incompatíveis'
                }}
            self.uom_id = self.invoice_line_id.product_id.uom_po_id
            self.product_id = self.invoice_line_id.product_id
            if self.invoice_line_id.cfop_id:
                self.cfop_id = self.invoice_line_id.cfop_id

    @api.onchange('product_id')
    def product_onchange(self):
        if self.product_id.uom_po_id and self.uom_id:
            if self.product_id.uom_po_id.category_id.id != self.uom_id.category_id.id:
                return {'value': {},
                        'warning': {'title': 'Atenção',
                                    'message': u'Unidades de medida incompatíveis'}}
        self.uom_id = self.product_id.uom_po_id.id

    @api.onchange('uom_id')
    def uom_onchange(self):
        if self.product_id.uom_po_id and self.uom_id:
            if self.product_id.uom_po_id.category_id.id != self.uom_id.category_id.id:
                return {'value': {},
                        'warning': {'title': 'Atenção',
                                    'message': u'Unidades de medida incompatíveis'}}
