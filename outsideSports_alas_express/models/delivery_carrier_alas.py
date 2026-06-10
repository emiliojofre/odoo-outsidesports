# -*- coding: utf-8 -*-
import json
import logging
import requests
import base64

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

ALAS_API_BASE_URL = 'https://ws.alasxpress.com/api'

# Mapeo de estados Alas Express → estado legible
ALAS_STATUS_MAP = {
    'Planificación': 'draft',
    'Recepción Física': 'in_transit',
    'Entrega Agendada': 'in_transit',
    'Entrega Reagendada': 'in_transit',
    'Rechazado Agendamiento': 'canceled',
    'Entrega Ruteada': 'in_transit',
    'En Ruta': 'in_transit',
    'Entregado': 'delivered',
    'Rechazado Terreno': 'canceled',
    'No Entregable': 'canceled',
}


class ProviderAlasExpress(models.Model):
    _inherit = 'delivery.carrier'

    delivery_type = fields.Selection(
        selection_add=[('alas_express', 'Alas Express')],
        ondelete={'alas_express': 'set default'},
    )

    # ── Configuración de la API ─────────────────────────────────────────────
    alas_api_key = fields.Char(
        string='API Key (x-alas-ce0-api-key)',
        help='API Key proporcionada por Alas Express para autenticación.',
    )
    alas_partner = fields.Char(
        string='Partner',
        help='Nombre del Partner configurado en Alas Express para este cliente B2B.',
    )
    alas_sender_code = fields.Char(
        string='RUT Empresa (Sender Code)',
        help='RUT del cliente B2B que envía las órdenes de entrega (ej: 12345678-5).',
    )
    alas_sender_location = fields.Char(
        string='Bodega (Sender Location)',
        help='Código de bodega del cliente B2B (opcional, ej: 0cf67dbf).',
    )
    alas_dispatch_labels = fields.Boolean(
        string='Enviar etiquetas por correo',
        default=True,
        help='Si está activo, Alas enviará las etiquetas por correo al cliente B2B.',
    )
    alas_labels_sync = fields.Boolean(
        string='Recibir etiquetas en creación (Base64)',
        default=True,
        help='Si está activo, las etiquetas se retornan en Base64 al crear la orden.',
    )
    alas_ampm_service = fields.Boolean(
        string='Servicio AM/PM',
        default=False,
        help='Activa el servicio de entrega con franja horaria AM/PM.',
    )
    alas_big_ticket = fields.Boolean(
        string='Big Ticket',
        default=False,
        help='Activa cuando el envío es de tamaño superior al normado.',
    )
    alas_add_insurance = fields.Boolean(
        string='Agregar seguro adicional',
        default=False,
    )
    alas_lob_type = fields.Integer(
        string='Tipo de Negocio (LOB)',
        default=1,
        help='Tipo de línea de negocio para Alas Express.',
    )

    # ── Helpers internos ────────────────────────────────────────────────────

    def _alas_get_headers(self):
        """Retorna los headers de autenticación para la API."""
        self.ensure_one()
        if not self.alas_api_key:
            raise UserError(_(
                'No se ha configurado la API Key de Alas Express en el método de envío "%s".'
            ) % self.name)
        return {
            'Content-Type': 'application/json',
            'x-alas-ce0-api-key': self.alas_api_key,
        }

    def _alas_call(self, method, endpoint, payload=None):
        """
        Realiza una llamada a la API de Alas Express.
        Retorna el dict de respuesta o lanza UserError ante error HTTP.
        """
        url = f'{ALAS_API_BASE_URL}{endpoint}'
        headers = self._alas_get_headers()
        try:
            resp = requests.request(
                method,
                url,
                headers=headers,
                json=payload,
                timeout=30,
            )
            _logger.debug('Alas Express [%s %s] → %s: %s', method, endpoint, resp.status_code, resp.text)
        except requests.exceptions.Timeout:
            raise UserError(_('Tiempo de espera agotado al conectar con Alas Express.'))
        except requests.exceptions.ConnectionError as e:
            raise UserError(_('Error de conexión con Alas Express: %s') % str(e))

        if resp.status_code in (200, 201):
            try:
                return resp.json()
            except ValueError:
                return {}

        # Manejo de errores conocidos de la API
        try:
            error_body = resp.json()
            msg = error_body.get('message') or error_body.get('errors') or resp.text
        except ValueError:
            msg = resp.text

        # Log del payload para debugging
        _logger.error('Alas Express ERROR payload enviado: %s', json.dumps(payload, ensure_ascii=False) if payload else 'N/A')

        raise UserError(_(
            'Error %s de Alas Express en %s:\n%s\n\nPayload enviado:\n%s'
        ) % (resp.status_code, endpoint, msg, json.dumps(payload, indent=2, ensure_ascii=False) if payload else 'N/A'))
    # ── Construcción del payload ─────────────────────────────────────────────

    def _alas_build_delivery_order_payload(self, picking):
        """
        Construye el payload para crear una Delivery Order en Alas Express
        a partir de un stock.picking de Odoo.
        """
        self.ensure_one()
        partner = picking.partner_id
        if not partner:
            raise UserError(_('El albarán "%s" no tiene un destinatario configurado.') % picking.name)

        # Validaciones mínimas
        if not partner.street:
            raise UserError(_('El destinatario "%s" no tiene calle configurada.') % partner.name)
        if not partner.city:
            raise UserError(_('El destinatario "%s" no tiene ciudad/comuna configurada.') % partner.name)

        # Teléfono móvil: limpiar y validar 9 dígitos
        mobile = (partner.mobile or partner.phone or '').replace(' ', '').replace('+56', '').replace('-', '')
        if not mobile:
            raise UserError(_('El destinatario "%s" no tiene teléfono configurado.') % partner.name)
        # Tomar solo los últimos 9 dígitos
        mobile = mobile[-9:]
        if len(mobile) != 9:
            raise UserError(_(
                'El teléfono del destinatario "%s" debe tener 9 dígitos (sin código de país): %s'
            ) % (partner.name, mobile))

        # Separar nombre y apellido
        name_parts = (partner.name or '').strip().split(' ', 1)
        first_name = name_parts[0][:50]
        last_name = (name_parts[1] if len(name_parts) > 1 else first_name)[:50]

        # Separar calle y número
        street_parts = (partner.street or '').strip().rsplit(' ', 1)
        if len(street_parts) == 2 and street_parts[1].isdigit():
            street = street_parts[0][:150]
            number = street_parts[1][:50]
        else:
            street = (partner.street or '')[:150]
            number = (partner.street2 or 'S/N')[:50]

        # Códigos de paquetes: uno por unidad de movimiento o por nombre de picking
        products_codes = self._alas_get_package_codes(picking)

        payload = {
            'partner': self.alas_partner or '',
            'deliveryOrderCode': picking.name,
            'senderCode': self.alas_sender_code or '',
            'receiverFirstName': first_name,
            'receiverLastName': last_name,
            'receiverMobilePhone': mobile,
            'destinationCity': partner.city or '',
            'destinationStreet': street,
            'destinationNumber': number,
            'productsCodes': products_codes,
            'dispatchLabels': self.alas_dispatch_labels,
            'deliveryLabelsSync': self.alas_labels_sync,
            'lobType': self.alas_lob_type or 1,
            'bigTicket': self.alas_big_ticket,
            'addInsurance': self.alas_add_insurance,
        }

        # Opcionales
        if self.alas_sender_location:
            payload['senderLocation'] = self.alas_sender_location
        if partner.email:
            payload['receiverEmail'] = partner.email
        if partner.vat:
            payload['receiverCode'] = partner.vat
        if self.alas_ampm_service:
            payload['ampmService'] = True

        return payload

    def _alas_get_package_codes(self, picking):
        """
        Genera los códigos de paquetes para la orden.
        Si el picking tiene paquetes de producto definidos, usa sus nombres.
        Si no, genera un código por línea de movimiento: PICKING-LINE_INDEX.
        """
        if picking.package_ids:
            return [pkg.name for pkg in picking.package_ids]

        # Fallback: un paquete por unidad de demanda (máx. práctico)
        codes = []
        for idx, move in enumerate(picking.move_ids.filtered(lambda m: m.state not in ('cancel', 'draft')), start=1):
            qty = int(move.product_uom_qty)
            for i in range(max(qty, 1)):
                codes.append(f'{picking.name}-{idx}-{i+1}')
        return codes if codes else [picking.name]

    # ── Métodos públicos de la API ───────────────────────────────────────────

    def alas_create_delivery_order(self, picking):
        """
        Crea la Delivery Order en Alas Express para el picking dado.
        Guarda el ID retornado y la etiqueta en el picking.
        """
        self.ensure_one()
        payload = self._alas_build_delivery_order_payload(picking)
        _logger.info('Alas Express - Creando orden para picking %s: %s', picking.name, payload)

        result = self._alas_call('POST', '/delivery-orders', payload)

        alas_id = result.get('deliveryOrderId', '')
        labels_url = result.get('labelsUrl', '')
        label_b64 = result.get('deliveryLabelsBase64', '')
        package_codes = result.get('deliveryOrderPackageCodes', '')

        picking.write({
            'alas_delivery_order_id': alas_id,
            'alas_labels_url': labels_url,
            'alas_package_codes': package_codes,
            'alas_status': 'Planificación',
        })

        # Guardar etiqueta si viene en la respuesta
        if label_b64:
            self._alas_save_label_attachment(picking, label_b64)

        return result

    def alas_get_status(self, picking):
        """
        Consulta el estado de la Delivery Order en Alas Express.
        Actualiza el campo alas_status del picking.
        """
        self.ensure_one()
        if not picking.alas_delivery_order_id:
            raise UserError(_('El albarán "%s" no tiene un ID de Alas Express asignado.') % picking.name)

        # Consulta por GET usando el ID de Alas
        result = self._alas_call('GET', f'/delivery-orders/{picking.alas_delivery_order_id}')

        status = result.get('status', '')
        description = result.get('description', '')
        delivery_expected = result.get('deliveryExpected', '')

        picking.write({
            'alas_status': status,
            'alas_delivery_expected': delivery_expected or False,
        })

        return result

    def alas_get_label(self, picking):
        """
        Obtiene/regenera la etiqueta de Alas Express para el picking.
        Devuelve el PDF en Base64.
        """
        self.ensure_one()
        if not picking.alas_delivery_order_id:
            raise UserError(_('El albarán "%s" no tiene un ID de Alas Express asignado.') % picking.name)

        payload = {
            'partner': self.alas_partner or '',
            'senderCode': self.alas_sender_code or '',
            'deliveryOrderCode': picking.name,
        }
        result = self._alas_call('POST', '/delivery-orders/label', payload)
        label_b64 = result.get('deliveryLabelsBase64', '')
        if label_b64:
            self._alas_save_label_attachment(picking, label_b64)
        return result

    def alas_get_label_zpl(self, picking):
        """Obtiene etiqueta en formato ZPL."""
        self.ensure_one()
        if not picking.alas_delivery_order_id:
            raise UserError(_('El albarán "%s" no tiene un ID de Alas Express asignado.') % picking.name)

        payload = {
            'partner': self.alas_partner or '',
            'senderCode': self.alas_sender_code or '',
            'deliveryOrderCode': picking.name,
        }
        result = self._alas_call('POST', '/delivery-orders/label-zpl', payload)
        label_b64 = result.get('deliveryLabelsBase64', '')
        if label_b64:
            self._alas_save_label_attachment(picking, label_b64, suffix='_zpl')
        return result

    def alas_reject_order(self, picking):
        """
        Rechaza una Delivery Order en Alas Express.
        Solo válido antes de ciertos estados.
        """
        self.ensure_one()
        if not picking.alas_delivery_order_id:
            raise UserError(_('El albarán "%s" no tiene un ID de Alas Express asignado.') % picking.name)

        payload = {
            'partner': self.alas_partner or '',
            'senderCode': self.alas_sender_code or '',
            'deliveryOrderCode': picking.name,
        }
        result = self._alas_call('POST', '/delivery-orders/reject', payload)
        picking.write({'alas_status': result.get('status', 'Rechazada B2B')})
        return result

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _alas_save_label_attachment(self, picking, label_b64, suffix=''):
        """Guarda el PDF de etiqueta como adjunto del picking."""
        try:
            pdf_data = base64.b64decode(label_b64)
        except Exception:
            _logger.warning('Alas Express: no se pudo decodificar el Base64 de la etiqueta.')
            return

        filename = f'alas_label_{picking.name}{suffix}.pdf'
        # Eliminar adjunto anterior con mismo nombre
        existing = self.env['ir.attachment'].search([
            ('res_model', '=', 'stock.picking'),
            ('res_id', '=', picking.id),
            ('name', '=', filename),
        ])
        existing.unlink()

        self.env['ir.attachment'].create({
            'name': filename,
            'type': 'binary',
            'datas': label_b64,
            'res_model': 'stock.picking',
            'res_id': picking.id,
            'mimetype': 'application/pdf',
        })
        _logger.info('Alas Express: etiqueta guardada como adjunto "%s" en picking %s.', filename, picking.name)

    # ── Métodos heredados delivery.carrier ───────────────────────────────────

    def alas_express_rate_shipment(self, order):
        """Estimación de tarifa (no soportada por la API, retorna 0)."""
        return {
            'success': True,
            'price': 0.0,
            'error_message': False,
            'warning_message': False,
        }

    def alas_express_send_shipping(self, pickings):
        """
        Método estándar de Odoo para enviar un envío.
        Crea la Delivery Order en Alas Express y retorna el tracking.
        """
        result = []
        for picking in pickings:
            try:
                response = self.alas_create_delivery_order(picking)
                result.append({
                    'exact_price': 0.0,
                    'tracking_number': response.get('deliveryOrderId', ''),
                })
            except UserError as e:
                raise
            except Exception as e:
                _logger.exception('Alas Express: error inesperado al crear orden para %s', picking.name)
                raise UserError(_('Error inesperado al enviar a Alas Express: %s') % str(e))
        return result

    def alas_express_get_tracking_link(self, picking):
        """URL de tracking para el cliente final."""
        if picking.carrier_tracking_ref:
            return f'https://www.alasxpress.com/?tracking={picking.carrier_tracking_ref}'
        return False

    def alas_express_cancel_shipment(self, pickings):
        """Cancela/rechaza la orden en Alas Express."""
        for picking in pickings:
            try:
                self.alas_reject_order(picking)
            except UserError as e:
                _logger.warning('Alas Express - No se pudo rechazar %s: %s', picking.name, e)

    def alas_express_get_default_custom_package_code(self):
        return False
