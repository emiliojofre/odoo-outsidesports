# -*- coding: utf-8 -*-
from odoo import models, fields, _
from .alasxpress_service import AlasxpressService

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    alas_delivery_id = fields.Char(string="Alasxpress ID", copy=False, readonly=True)

    def action_alas_get_status(self):
        self.ensure_one()
        if not self.alas_delivery_id or not self.carrier_id:
            return
            
        api = AlasxpressService(self.carrier_id.alas_api_key, self.carrier_id.alas_api_url)
        status_data = api.get_status(self.alas_delivery_id)
        
        if status_data:
            estado = status_data.get('status', 'Desconocido')
            self.message_post(body=f"Estado actual en Alasxpress: {estado}")

    def action_alas_cancel(self):
        self.ensure_one()
        if not self.alas_delivery_id or not self.carrier_id:
            return

        api = AlasxpressService(self.carrier_id.alas_api_key, self.carrier_id.alas_api_url)
        res = api.reject(self.alas_delivery_id, "Cancelado desde Odoo")
        
        if res.get('success'):
            self.message_post(body="Orden rechazada en Alasxpress.")
        else:
            msg = res.get('message', 'Error desconocido')
            self.message_post(body=f"Fallo al anular: {msg}")