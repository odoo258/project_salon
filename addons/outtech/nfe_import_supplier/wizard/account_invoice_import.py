# coding=utf-8
# ###########################################################################
#
#    Author: Luis Felipe Mileo
#            Fernando Marcato Rodrigues
#            Daniel Sadamo Hirayama
#            Danimar Ribeiro <danimaribeiro@gmail.com>
#    Copyright 2015 KMEE - www.kmee.com.br
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

import os
import logging
import cPickle
from odoo import models, fields, api
from odoo.tools.translate import _
#from openerp.addons.nfe.sped.nfe.nfe_factory import NfeFactory
from odoo.exceptions import Warning
from datetime import date

from ..service.nfe_serializer import NFeSerializer


_logger = logging.getLogger(__name__)


class NfeImportAccountInvoiceImport(models.TransientModel):
    """
        Assistente de importaçao de txt e xml
    """
    _name = 'nfe_import.account_invoice_import'
    _description = 'Import Eletronic Document in TXT and XML format'

    def _default_company(self):
        return self.env.user.company_id

    company_id = fields.Many2one('res.company', string="Empresa",
                                 default=_default_company)

    state = fields.Selection([('init', 'init'), ('done', 'done')],
                             string='state', readonly=True, default='init')
    edoc_input = fields.Binary(u'Arquivo do documento eletrônico',
                               help=u'Somente arquivos no formato TXT e XML')
    file_name = fields.Char('File Name', size=128)
    create_partner = fields.Boolean(
        u'Criar fornecedor automaticamente?', default=True,
        help=u'Cria o fornecedor automaticamente caso não esteja cadastrado')
    account_invoice_id = fields.Many2one('account.invoice',u'Fatura de compra', domain="[('state','=','draft')]")
    supplier_partner_id = fields.Many2one('res.partner', string=u"Parceiro")
    warehouse_id = fields.Many2one('stock.warehouse','Warehouse', required=True, domain="[('company_id','=', company_id)]")

    journal_id = fields.Many2one('account.journal','Journal', required=True, domain="[('type','=','purchase')]")
                                          #,related="account_invoice_id.partner_id")
    # fiscal_category_id = fields.Many2one(
    #     'l10n_br_account.fiscal.category', 'Categoria Fiscal')
    fiscal_position = fields.Many2one('account.fiscal.position', 'Posição Fiscal')

    @api.onchange('account_invoice_id')
    def onchange_account_invoice(self):
        if self.account_invoice_id:
            self.fiscal_position = self.account_invoice_id.fiscal_position_id.id
        return False

    def _check_extension(self, filename):
        if not filename:
            raise Warning(_('Please select a correct XML file'))
        (__, ftype) = os.path.splitext(filename)
        if ftype.lower() not in ('.xml'):
            raise Warning(_('Please select a correct XML file'))
        return ftype

    # def _get_nfe_factory(self, nfe_version):
    #     return NfeFactory().get_nfe(nfe_version)

    def _validate_against_invoice(self, invoice_values, invoice):
        if 'invoice_line' in invoice_values:
            if len(invoice_values['invoice_line']) != len(invoice.invoice_line_ids):
                raise Exception(
                    u'O xml não possui o mesmo número de itens da fatura')
        else:
            if len(invoice_values['invoice_line_ids']) != len(invoice.invoice_line_ids):
                raise Exception(
                    u'O xml não possui o mesmo número de itens da fatura')
        if "cnpj_cpf" in invoice_values:
            if invoice_values["cnpj_cpf"] != invoice.partner_id.cnpj_cpf:
                raise Exception(
                    u'O CNPJ não corresponde ao fornecedor da fatura')
        else:
            if invoice_values["partner_id"] != invoice.partner_id.id:
                raise Exception(
                    u'O CNPJ não corresponde ao fornecedor da fatura')

    @api.multi
    def import_edoc(self):
        try:
            self.ensure_one()
            importer = self[0]

            ftype = self._check_extension(importer.file_name)

            nfe_serializer = NFeSerializer()
            eDoc = nfe_serializer.import_edoc(self.env, importer.edoc_input)[0]

            inv_values = eDoc['values']
            if self.account_invoice_id:
                self._validate_against_invoice(
                    inv_values,
                    self.account_invoice_id)

            if importer.create_partner and inv_values['partner_id'] == False:
                part = self.env['res.partner'].search(['|',('cnpj_cpf','=',inv_values['partner_values']['cnpj_cpf']),('inscr_est','=',inv_values['partner_values']['inscr_est'])])
                if part:
                    raise Exception(u'Fonrcedor %s cadastrado com mesmo CNPJ ou Inscricao Estadual' % part.name)
                try:
                    partner = self.env['res.partner'].create(
                        inv_values['partner_values'])
                except Exception,e:
                    raise Exception(e[0])
                inv_values['partner_id'] = partner.id
                inv_values['account_id'] = partner.property_account_payable_id.id
            elif inv_values['partner_id'] == False:
                raise Exception(
                    u'Fornecedor não cadastrado, o xml não será importado\n'
                    u'Marque a opção "Criar fornecedor" se deseja importar '
                    u'mesmo assim')

            inv_values['fiscal_position_id'] = importer.fiscal_position.id
            # inv_values['journal_id'] = \
            #     importer.fiscal_category_id.property_journal.id

            product_import_ids = []
            line_ids = ()

            for inv_line in inv_values['invoice_line']:
                inv_line[2]['fiscal_position_id'] = importer.fiscal_position.id

                # inv_line = self.fiscal_position.get_fiscal_position(partner.id, delivery_id=partner.id)(
                #     inv_line[2])

                inv_vals = {
                    'product_id': inv_line[2]['product_id'],
                    'uom_id': inv_line[2]['uos_id'],
                    'code_product_xml': inv_line[2]['product_code_xml'],
                    'uom_xml': inv_line[2]['uom_xml'],
                    'product_xml': inv_line[2]['product_name_xml'],
                    'cfop_id': inv_line[2]['cfop_id'],
                    'cfop_xml': inv_line[2]['cfop_xml'],
                    'quantity_xml': inv_line[2]['quantity'],
                    'unit_amount_xml': inv_line[2]['price_unit'],
                    'discount_total_xml': inv_line[2]['valor_desconto'],
                    'total_amount_xml': inv_line[2]['price_gross']
                }

                if self.account_invoice_id:
                    line = self.account_invoice_id.invoice_line_ids.filtered(
                        lambda x: x.product_id.id == inv_vals['product_id'] and
                        x.quantity == inv_vals['quantity_xml'] and
                        x.id not in line_ids)
                    if line:
                        line_ids += (line[0].id,)
                        inv_vals['invoice_line_id'] = line[0].id

                product_import_ids.append((0, 0, inv_vals))

            values = {
                'supplier_id': inv_values['partner_id'],
                'import_from_invoice': True if importer.account_invoice_id else False,
                'account_invoice_id': importer.account_invoice_id.id,
                # 'fiscal_category_id': importer.fiscal_category_id.id,
                'fiscal_position': importer.fiscal_position.id,
                'journal_id': importer.journal_id.id,
                'warehouse_id':importer.warehouse_id.id,
                'number': inv_values['vendor_number'],
                'natureza_operacao': inv_values['nat_op'],
                'amount_total': inv_values['amount_total'],
                'xml_data': cPickle.dumps(inv_values),
                'product_import_ids': product_import_ids,
                'edoc_input': importer.edoc_input,
                'file_name': importer.file_name,
                'date': date.today()
            }

            import_edit = self.env['nfe.import.edit'].create(values)

            dummy, view_id = self.env['ir.model.data'].get_object_reference('nfe_import_supplier', 'nfe_import_edit_form')

            return {
                'name':_("Change Credit Card"),
                'view_mode': 'form',
                'view_id': view_id,
                'view_type': 'form',
                'res_id': import_edit.id,
                'res_model': 'nfe.import.edit',
                'type': 'ir.actions.act_window',

            }
            # action_obj = self.env['ir.actions.act_window']
            # action_id = model_obj.get_object_reference('nfe_import_supplier', 'action_nfe_import_edit_form')[1]
            # res = action_obj.read(action_id)
            # res['res_id'] = import_edit.id
            # return res
        except Exception as e:
            if isinstance(e.message, unicode):
                _logger.error(e.message, exc_info=True)
                raise Warning(
                    u'Erro ao tentar importar o xml\n'
                    u'Mensagem de erro:\n{0}'.format(
                        e.message))
            elif isinstance(e.message, str):
                _logger.error(
                    e.message.decode(
                        'utf-8',
                        'ignore'),
                    exc_info=True)
            else:
                _logger.error(str(e), exc_info=True)
            raise Warning(
                u'Erro ao tentar importar o xml\n'
                u'Mensagem de erro:\n{0}'.format(
                    e.message.decode('utf-8', 'ignore')))

    @api.multi
    def done(self, cr, uid, ids, context=False):
        return True
