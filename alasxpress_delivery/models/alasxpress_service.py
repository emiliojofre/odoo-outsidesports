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
        """ Recibe el objeto picking de Odoo y construye el JSON para Alasxpress """
        
        # Dividir nombre con seguridad
        name = picking.partner_id.name or ""
        name_parts = name.split(" ", 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else "."

        # Construcción del payload según los errores del log anterior
        payload = {
            "deliveryOrderCode": picking.name,
            "senderCode": picking.company_id.name[:20], # Truncar por si acaso
            "partner": "OUTSIDE_SPORTS", 
            "receiverFirstName": first_name,
            "receiverLastName": last_name,
            "receiverMobilePhone": picking.partner_id.mobile or picking.partner_id.phone or "999999999",
            "destinationStreet": picking.partner_id.street or "Sin Direccion",
            "destinationNumber": "S/N",
            "destinationCity": picking.partner_id.city or "Santiago",
            "productsCodes": ",".join([line.product_id.default_code or 'N/A' for line in picking.move_ids_without_package]),
        }

        _logger.info("### ENVIANDO A ALASXPRESS: %s", json.dumps(payload))
        
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