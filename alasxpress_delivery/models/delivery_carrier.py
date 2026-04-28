from odoo import models, fields, api, _
from odoo.exceptions import UserError
from .alasxpress_service import AlasxpressService
import base64

class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    delivery_type = fields.Selection(selection_add=[
        ('alasxpress', 'Alasxpress')
    ], ondelete={'alasxpress': 'set default'})
    
    alas_api_key = fields.Char("Alasxpress API Key")
    alas_api_url = fields.Char("API URL", default="https://ws.alasxpress.com/api")
    alas_use_zpl = fields.Boolean("Usar formato ZPL", help="Si se marca, descargara etiquetas ZPL en lugar de PDF")

    def alasxpress_send_shipping(self, pickings):
        res = []
        for picking in pickings:
            api_client = AlasxpressService(self.alas_api_key, self.alas_api_url)
            
            # PASAMOS EL OBJETO PICKING DIRECTO
            order_res = api_client.create_order(picking)
            
            if order_res.get('success') or 'id' in order_res:
                # Si la API devuelve un ID, lo guardamos
                alas_id = order_res.get('id') or order_res.get('deliveryOrderId')
                picking.alas_delivery_id = str(alas_id)
                
                shipping_data = {
                    'exact_price': 0.0,
                    'tracking_number': picking.alas_delivery_id
                }
                res.append(shipping_data)
            else:
                msg = order_res.get('message', 'Error desconocido en Alasxpress')
                raise UserError(f"Error Alasxpress: {msg}")
        return res

    def alasxpress_cancel_shipment(self, pickings):
        api_client = AlasxpressService(self.alas_api_key, self.alas_api_url)
        for picking in pickings:
            if picking.alas_delivery_id:
                api_client.reject(picking.alas_delivery_id)
        return True