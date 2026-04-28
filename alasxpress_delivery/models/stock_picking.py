# -*- coding: utf-8 -*-
from odoo import models, fields, _
from .alasxpress_service import AlasxpressService

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    alas_delivery_id = fields.Char("Alasxpress ID", copy=False)

    def action_alas_get_status(self):
        """
        Consulta el estado actual de la orden directamente desde la API
        y lo registra en el chatter.
        """
        self.ensure_one()
        if not self.alas_delivery_id:
            return
            
        carrier = self.carrier_id
        if not carrier or carrier.delivery_type != 'alasxpress':
            return

        api = AlasxpressService(carrier.alas_api_key, carrier.alas_api_url)
        status_data = api.get_status(self.alas_delivery_id)
        
        if status_data:
            estado = status_data.get('status', 'Desconocido')
            self.message_post(body=f"Estado actual en Alasxpress: {estado}")
        else:
            self.message_post(body="No se pudo obtener el estado desde Alasxpress.")

    def action_alas_cancel(self):
        """
        Envia una peticion de rechazo/anulacion a la API de Alasxpress.
        """
        self.ensure_one()
        if not self.alas_delivery_id:
            return

        carrier = self.carrier_id
        api = AlasxpressService(carrier.alas_api_key, carrier.alas_api_url)
        
        # Llamada al metodo reject definido en alasxpress_service.py
        res = api.reject(self.alas_delivery_id, "Cancelado desde Odoo")
        
        if res.get('success'):
            self.message_post(body="Orden rechazada/anulada exitosamente en Alasxpress.")
        else:
            msg = res.get('message', 'Error desconocido')
            self.message_post(body=f"Fallo al anular en Alasxpress: {msg}")