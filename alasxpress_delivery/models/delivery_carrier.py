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
        api_client = AlasxpressService(self.alas_api_key, self.alas_api_url)
        
        for picking in pickings:
            payload = {
                "external_id": picking.name,
                "receiver": {
                    "name": picking.partner_id.name,
                    "address": f"{picking.partner_id.street} {picking.partner_id.street2 or ''}",
                    "city": picking.partner_id.city,
                    "phone": picking.partner_id.phone or picking.partner_id.mobile,
                },
                "items": [{"sku": l.product_id.default_code, "qty": l.qty_done} for l in picking.move_line_ids]
            }
            
            order_res = api_client.create_order(payload)
            if not order_res.get('success'):
                raise UserError(_("Error Alasxpress: %s") % order_res.get('message'))

            delivery_id = order_res.get('deliveryOrderId')
            tracking_num = order_res.get('trackingNumber')
            
            label_res = api_client.get_label(delivery_id, zpl=self.alas_use_zpl)
            
            logmessage = (_("Envio creado en Alasxpress: %s") % tracking_num)
            picking.message_post(body=logmessage, attachments=[
                (f'label_{tracking_num}.{"zpl" if self.alas_use_zpl else "pdf"}', label_res.content)
            ])

            picking.alas_delivery_id = delivery_id
            res.append({'exact_price': 0.0, 'tracking_number': tracking_num})
            
        return res

    def alasxpress_cancel_shipment(self, pickings):
        api_client = AlasxpressService(self.alas_api_key, self.alas_api_url)
        for picking in pickings:
            if picking.alas_delivery_id:
                api_client.reject(picking.alas_delivery_id)
        return True