# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    # ── Campo auxiliar para visibilidad en vistas (attrs no acepta x.y en Odoo 16) ──
    alas_is_carrier = fields.Boolean(
        string='Es Alas Express',
        compute='_compute_alas_is_carrier',
        store=False,
    )

    @api.depends('carrier_id', 'carrier_id.delivery_type')
    def _compute_alas_is_carrier(self):
        for rec in self:
            rec.alas_is_carrier = rec.carrier_id.delivery_type == 'alas_express'

    # ── Campos Alas Express ──────────────────────────────────────────────────
    alas_delivery_order_id = fields.Char(
        string='ID Alas Express',
        copy=False,
        readonly=True,
        help='Identificador de la Delivery Order asignado por Alas Express.',
    )
    alas_labels_url = fields.Char(
        string='URL Etiquetas Alas',
        copy=False,
        readonly=True,
    )
    alas_package_codes = fields.Char(
        string='Códigos de Paquetes Alas',
        copy=False,
        readonly=True,
        help='Lista de códigos de paquetes asociados a la orden en Alas Express.',
    )
    alas_status = fields.Char(
        string='Estado Alas Express',
        copy=False,
        readonly=True,
        help='Último estado sincronizado desde Alas Express.',
    )
    alas_delivery_expected = fields.Datetime(
        string='Entrega Estimada Alas',
        copy=False,
        readonly=True,
    )
    alas_status_color = fields.Integer(
        string='Color Estado',
        compute='_compute_alas_status_color',
        store=False,
    )

    # ── Computados ───────────────────────────────────────────────────────────

    @api.depends('alas_status')
    def _compute_alas_status_color(self):
        """Asigna un color semáforo según el estado de Alas."""
        COLOR_MAP = {
            'Planificación': 0,           # gris
            'Recepción Física': 3,        # amarillo
            'Entrega Agendada': 3,        # amarillo
            'Entrega Reagendada': 3,      # amarillo
            'Entrega Ruteada': 4,         # verde claro
            'En Ruta': 10,               # verde
            'Entregado': 10,             # verde
            'Rechazado Agendamiento': 1,  # rojo
            'Rechazado Terreno': 1,       # rojo
            'No Entregable': 1,           # rojo
        }
        for rec in self:
            rec.alas_status_color = COLOR_MAP.get(rec.alas_status, 0)

    # ── Acciones desde el picking ────────────────────────────────────────────

    def action_alas_send_order(self):
        """Crea la Delivery Order en Alas Express desde el picking."""
        self.ensure_one()
        carrier = self.carrier_id
        if not carrier or carrier.delivery_type != 'alas_express':
            raise UserError(_(
                'El método de envío del albarán "%s" no es Alas Express.'
            ) % self.name)
        if self.alas_delivery_order_id:
            raise UserError(_(
                'Este albarán ya tiene una orden en Alas Express (ID: %s).\n'
                'Para crear una nueva, primero rechace la actual.'
            ) % self.alas_delivery_order_id)

        carrier.alas_create_delivery_order(self)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'main',
        }

    def action_alas_get_status(self):
        """Actualiza el estado de la orden desde Alas Express."""
        self.ensure_one()
        carrier = self.carrier_id
        if not carrier or carrier.delivery_type != 'alas_express':
            raise UserError(_('El método de envío no es Alas Express.'))

        carrier.alas_get_status(self)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'main',
        }

    def action_alas_get_label(self):
        """Obtiene/regenera la etiqueta PDF desde Alas Express."""
        self.ensure_one()
        carrier = self.carrier_id
        if not carrier or carrier.delivery_type != 'alas_express':
            raise UserError(_('El método de envío no es Alas Express.'))

        carrier.alas_get_label(self)
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Etiqueta Alas Express'),
                'message': _('Etiqueta generada y guardada como adjunto del albarán.'),
                'type': 'success',
                'sticky': False,
            },
        }

    def action_alas_get_label_zpl(self):
        """Obtiene la etiqueta en formato ZPL desde Alas Express."""
        self.ensure_one()
        carrier = self.carrier_id
        if not carrier or carrier.delivery_type != 'alas_express':
            raise UserError(_('El método de envío no es Alas Express.'))

        carrier.alas_get_label_zpl(self)
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Etiqueta ZPL Alas Express'),
                'message': _('Etiqueta ZPL guardada como adjunto del albarán.'),
                'type': 'success',
                'sticky': False,
            },
        }

    def action_alas_reject_order(self):
        """Rechaza la Delivery Order en Alas Express."""
        self.ensure_one()
        carrier = self.carrier_id
        if not carrier or carrier.delivery_type != 'alas_express':
            raise UserError(_('El método de envío no es Alas Express.'))

        carrier.alas_reject_order(self)
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Alas Express'),
                'message': _('Orden rechazada. Estado: %s') % self.alas_status,
                'type': 'warning',
                'sticky': False,
            },
        }

    def action_alas_open_label_attachment(self):
        """Abre el adjunto de la etiqueta PDF del picking, descargándolo si no existe."""
        self.ensure_one()
        attachment = self.env['ir.attachment'].search([
            ('res_model', '=', 'stock.picking'),
            ('res_id', '=', self.id),
            ('name', 'like', 'alas_label_'),
        ], order='create_date desc', limit=1)

        # Si no existe adjunto, intentar descargarlo ahora
        if not attachment:
            self.carrier_id.alas_get_label(self)
            attachment = self.env['ir.attachment'].search([
                ('res_model', '=', 'stock.picking'),
                ('res_id', '=', self.id),
                ('name', 'like', 'alas_label_'),
            ], order='create_date desc', limit=1)

        if not attachment:
            raise UserError(_('No se pudo obtener la etiqueta de Alas Express.'))

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'new',
        }

    # ── Cron / Actualización masiva de estado ────────────────────────────────

    def cron_alas_update_status(self):
        """
        Cron para actualizar el estado de todos los pickings con Alas Express
        que no estén en estado final.
        """
        FINAL_STATES = {'Entregado', 'Rechazado Agendamiento', 'Rechazado Terreno', 'No Entregable'}
        pickings = self.search([
            ('carrier_id.delivery_type', '=', 'alas_express'),
            ('alas_delivery_order_id', '!=', False),
            ('alas_status', 'not in', list(FINAL_STATES)),
            ('state', 'not in', ['cancel', 'done']),
        ])
        _logger.info('Alas Express cron: actualizando %d pickings', len(pickings))
        for picking in pickings:
            try:
                picking.carrier_id.alas_get_status(picking)
            except Exception as e:
                _logger.warning('Alas Express cron: error en picking %s → %s', picking.name, e)
