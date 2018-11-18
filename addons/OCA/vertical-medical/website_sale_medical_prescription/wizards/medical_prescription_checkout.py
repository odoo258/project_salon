# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _


import logging
_logger = logging.getLogger(__name__)


class MedicalPrescriptionCheckout(models.TransientModel):
    _name = 'medical.prescription.checkout'
    _description = 'Medical Prescription Checkout'

    order_id = fields.Many2one(
        string='Order',
        comodel_name='sale.order',
        default=lambda s: s._default_order_id(),
    )

    @api.model
    def _default_order_id(self):
        if self.env.context.get('active_model') != 'sale.order':
            return
        return self.env['sale.order'].browse(
            self.env.context.get('active_id')
        ).id

    @api.multi
    def action_process_data(self, **form_data):
        """ Process input data and create/update records
        :returns: Response dict {
            'error_fields': {
                'field_name': 'error string',
            },
            'errors': [
                'Generic, non-field specific error',
            ],
        }
        """

        self.ensure_one()

        error_fields = []
        res = {
            'error_fields': error_fields,
            'errors': [],
        }
        form_data = self._parse_form(form_data)

        for line_int_str, line_vals in form_data.iteritems():
            line_id = self.env['sale.order.line'].browse(int(line_int_str))
            # @TODO: A way to avoid this sudo? Seems secure enough though...
            line_id = line_id.sudo()
            if line_id.order_id != self.order_id:
                self._invalidate_all(line_vals, error_fields,
                                     name_prefix=line_int_str,
                                     )
                res['errors'].append(_(
                    'Cannot edit order line from another order'
                ))
                continue

            try:
                rx_line_vals = line_vals['prescription_order_line_id']
            except KeyError:
                res['errors'].append(_(
                    'Did not include prescription line information'
                ))
                continue

            if rx_line_vals.get('prescription_line_id', '0') != '0':
                rx_line_int = int(rx_line_vals['prescription_line_id'])
                line_id.write({
                    'prescription_order_line_id': rx_line_int,
                })
                continue

            medicament_id = line_id.product_id.medicament_ids[0]
            rx_line_vals.update({
                'medicament_id': medicament_id.id,
                'dispense_uom_id': medicament_id.uom_id.id,
                'qty': line_id.product_uom_qty,
            })

            name_prefix = '%s.prescription_order_line_id' % line_int_str

            try:
                patient_vals = rx_line_vals['patient_id']
            except KeyError:
                res['errors'].append(_(
                    'Did not include patient information'
                ))
                continue

            try:
                patient_vals.update({
                    'parent_id': line_id.order_id.partner_id.id,
                })
                rx_line_vals['patient_id'] = self._write_or_create(
                    'medical.patient', patient_vals,
                ).id
            except:
                res['errors'].append(_(
                    'Could not create patient'
                ))
                self._invalidate_all(
                    patient_vals, error_fields,
                    name_prefix='%s.patient_id' % name_prefix
                )
                continue

            try:
                physician_vals = rx_line_vals['physician_id']
            except KeyError:
                res['errors'].append(_(
                    'Did not include physician information'
                ))
                continue

            if int(physician_vals.get('id', 0)) == 0:
                try:
                    rx_line_vals['physician_id'] = self._write_or_create(
                        'medical.physician', physician_vals, write=False
                    ).id
                except:
                    _logger.exception("Could not create physician")
                    res['errors'].append(_(
                        'Could not create physician'
                    ))
                    self._invalidate_all(
                        physician_vals, error_fields,
                        name_prefix='%s.physician_id' % name_prefix
                    )
                    continue
            else:
                rx_line_vals['physician_id'] = physician_vals['id']

            try:
                rx_vals = line_vals['prescription_order_id']
            except KeyError:
                res['errors'].append(_(
                    'Did not include prescription information'
                ))
                continue

            if rx_vals.get('receive_method') != 'transfer':
                try:
                    del rx_vals['transfer_pharmacy_id']
                except KeyError:
                    pass

            try:
                transfer_vals = rx_vals['transfer_pharmacy_id']
                if int(transfer_vals.get('id', 0)) == 0:
                    rx_vals['transfer_pharmacy_id'] = self._write_or_create(
                        'medical.pharmacy', transfer_vals, write=False
                    ).id
            except KeyError:
                pass
            except:
                res['errors'].append(_(
                    'Could not create pharmacy'
                ))
                self._invalidate_all(
                    physician_vals, error_fields,
                    name_prefix='%s.transfer_pharmacy_id' % name_prefix
                )
                continue

            rx_vals['patient_id'] = rx_line_vals['patient_id']
            rx_vals['physician_id'] = rx_line_vals['physician_id']

            rx_line_vals['prescription_order_id'] = self._write_or_create(
                'medical.prescription.order', rx_vals,
            ).id
            rx_line_id = self._write_or_create(
                'medical.prescription.order.line', rx_line_vals,
            )

            line_id.write({'prescription_order_line_id': rx_line_id.id})

        return res

    @api.model
    def _write_or_create(self, model_name, vals, sudo_create=True,
                         write=True
                         ):
        model_obj = self.env[model_name]
        if write and int(vals.get('id', 0)) != 0:
            rec_id = model_obj.browse(int(vals['id']))
            del vals['id']
            rec_id.write(vals)
        else:
            if sudo_create:
                model_obj = model_obj.sudo()
            rec_id = model_obj.create(vals)
        return rec_id

    @api.model
    def _invalidate_all(self, obj, error_fields=None, name_prefix=None):
        if error_fields is None:
            error_fields = {}
        if name_prefix is None:
            name_prefix = ''
        for key, val in obj.iteritems():
            node_name = '%s.%s' % (name_prefix, key)
            if isinstance(val, dict):
                self._invalidate_all(val, error_fields, name_prefix=node_name)
            else:
                error_fields.append(node_name)
        return error_fields

    @api.model
    def _parse_form(self, vals):
        res = {}
        for key, val in vals.iteritems():
            split_names = key.split('.')
            data_obj = res
            for name_part in split_names[:-1]:
                try:
                    data_obj = data_obj[name_part]
                except KeyError:
                    data_obj[name_part] = {}
                    data_obj = data_obj[name_part]
            data_obj[split_names[-1]] = val
        return res
