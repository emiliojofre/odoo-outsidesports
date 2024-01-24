# -*- coding: utf-8 -*-

import json
import logging

from odoo import api, fields, models, _
from odoo.tools import float_compare

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    client_hes_ref = fields.Char('Referencia HES cliente')
    cliente_hes_date = fields.Date('Fecha HES cliente')
    oc_hes_required = fields.Boolean('OC y HES requeridos')
    
    def _create_invoices(self, grouped=False, final=False, date=None):

        invoices = super()._create_invoices(grouped=grouped, final=final, date=date)

        if self.is_subscription == False or self.oc_hes_required == True:
            order_oc = self.env['l10n_latam.document.type'].search([('code', '=', '801')],limit =1)
            order_hes = self.env['l10n_latam.document.type'].search([('code', '=', 'HES')],limit =1)
            for invoice in invoices:
                self.env['l10n_cl.account.invoice.reference'].create({
                    'origin_doc_number': self.client_order_ref,
                    'l10n_cl_reference_doc_type_id': order_oc.id,
                    'reason': 'ORDEN DE COMPRA',
                    'date': self.client_order_date,
                    'move_id': invoice.id
                })

                self.env['l10n_cl.account.invoice.reference'].create({
                    'origin_doc_number': self.client_hes_ref,
                    'l10n_cl_reference_doc_type_id': order_hes.id,
                    'reason': 'HOJA DE ENTRADA DE SERVICIOS',
                    'date': self.cliente_hes_date,
                    'move_id': invoice.id
                })
                
        return invoices