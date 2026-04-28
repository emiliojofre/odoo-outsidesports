import requests
import json
import logging

_logger = logging.getLogger(__name__)

class AlasxpressService:
    def __init__(self, api_key, url):
        self.api_key = api_key
        self.base_url = url.rstrip('/')

    def _headers(self):
        return {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

    def create_order(self, picking):
        """ Prepara el payload con los nombres de campos que la API exige """
        # Dividimos el nombre del cliente para First y Last Name
        name_parts = (picking.partner_id.name or "").split(" ", 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else "."

        payload = {
            "deliveryOrderCode": picking.name, # external_id -> deliveryOrderCode
            "senderCode": picking.company_id.name, # Requerido
            "partner": "OUTSIDE_SPORTS", # O el codigo de partner que te dio Alas
            "receiverFirstName": first_name,
            "receiverLastName": last_name,
            "receiverMobilePhone": picking.partner_id.mobile or picking.partner_id.phone or "",
            "destinationStreet": picking.partner_id.street or "",
            "destinationNumber": "S/N", # Si Odoo no tiene numero aparte, enviamos S/N
            "destinationCity": picking.partner_id.city or "",
            "productsCodes": ",".join([line.product_id.default_code or "" for line in picking.move_ids_without_package]),
        }
        
        # Log para verificar antes de enviar
        _logger.info("### NUEVO PAYLOAD CORREGIDO: %s", json.dumps(payload))
        
        url = f"{self.base_url}/delivery-orders"
        try:
            res = requests.post(url, headers=self._headers(), json=payload, timeout=20)
            return res.json()
        except Exception as e:
            return {'success': False, 'message': str(e)}

    def get_label(self, order_id, zpl=False):
        """ GET /delivery-orders/label o /delivery-orders/label-zpl """
        endpoint = "label-zpl" if zpl else "label"
        url = f"{self.base_url}/delivery-orders/{endpoint}?id={order_id}"
        return requests.get(url, headers=self._headers(), timeout=15)

    def get_status(self, order_id):
        """ GET /delivery-orders/status """
        url = f"{self.base_url}/delivery-orders/status?id={order_id}"
        res = requests.get(url, headers=self._headers())
        return res.json() if res.status_code == 200 else {}

    def reject(self, order_id, reason="Cancelado desde Odoo"):
        """ POST /delivery-orders/reject """
        url = f"{self.base_url}/delivery-orders/reject"
        payload = {"id": order_id, "reason": reason}
        res = requests.post(url, headers=self._headers(), json=payload)
        return res.json()