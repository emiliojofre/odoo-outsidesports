# -*- coding: utf-8 -*-
from odoo import models, fields, _
from .alasxpress_service import AlasxpressService

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    # Definimos el campo sin restricciones de grupo para evitar errores de vista
    alas_delivery_id = fields.Char(string="Alasxpress ID", copy=False, readonly=True)

    def action_alas_get_status(self):
        """ Consulta el estado en Alasxpress """
        self.ensure_one()
        # Validacion de seguridad para evitar errores si no hay ID o Carrier
        if not self.alas_delivery_id or not self.carrier_id:
            return
            
        try:
            api = AlasxpressService(self.carrier_id.alas_api_key, self.carrier_id.alas_api_url)
            status_data = api.get_status(self.alas_delivery_id)
            
            if status_data:
                estado = status_data.get('status', 'Desconocido')
                self.message_post(body=f"Estado actual en Alasxpress: {estado}")
        except Exception as e:
            self.message_post(body=f"Error al conectar con la API: {str(e)}")

    def action_alas_cancel(self):
        """ Solicita la anulacion en Alasxpress """
        self.ensure_one()
        if not self.alas_delivery_id or not self.carrier_id:
            return

        try:
            api = AlasxpressService(self.carrier_id.alas_api_key, self.carrier_id.alas_api_url)
            res = api.reject(self.alas_delivery_id, "Cancelado desde Odoo")
            
            if res and res.get('success'):
                self.message_post(body="Orden rechazada exitosamente en Alasxpress.")
            else:
                msg = res.get('message', 'Error desconocido') if res else 'Sin respuesta'
                self.message_post(body=f"Fallo al anular en Alasxpress: {msg}")
        except Exception as e:
            self.message_post(body=f"Error tecnico al intentar anular: {str(e)}")