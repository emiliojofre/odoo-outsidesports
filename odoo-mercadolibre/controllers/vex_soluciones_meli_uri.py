# controllers/main.py
from odoo import http
from odoo.http import request
import logging
import requests
import json

_logger = logging.getLogger(__name__)

class MeliLoginController(http.Controller):

    @http.route('/meli_login/ceralfasa', type='http', auth='public', website=True)
    def meli_login_ceralfasa_callback(self, **kwargs):
        code = kwargs.get('code')
        if not code:
            return "No se recibió el código de autorización"

        _logger.info(f"Recibido código de autorización: {code}")

        # Aquí podrías buscar el client_id y client_secret desde la config o db
        client_id = '4753009464781172'
        client_secret = 'hHMIm7TKCXJl0y6iVgAmMK2iG6b1eLKr'
        redirect_uri = 'https://ceralfa.odoo.com/meli_login/ceralfasa'

        try:
            # Hacer la petición POST para obtener el access_token
            response = requests.post(
                'https://api.mercadolibre.com/oauth/token',
                data={
                    'grant_type': 'authorization_code',
                    'client_id': client_id,
                    'client_secret': client_secret,
                    'code': code,
                    'redirect_uri': redirect_uri,
                },
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )

            result = response.json()

            if response.status_code == 200:
                access_token = result.get('access_token')
                _logger.info(f"Token de acceso obtenido: {access_token}")
                return f"Autenticación exitosa. Token: {access_token}"
            else:
                _logger.error(f"Error en autenticación: {result}")
                return f"Error al obtener el token: {result}"

        except Exception as e:
            _logger.exception("Excepción al obtener el token de acceso")
            return f"Excepción: {str(e)}"
        
    @http.route('/meli_login/cere', type='http', auth='public', website=True)
    def meli_login_cere_callback(self, **kwargs):
        code = kwargs.get('code')
        if not code:
            return "No se recibió el código de autorización"

        _logger.info(f"Recibido código de autorización: {code}")

        # Aquí podrías buscar el client_id y client_secret desde la config o db
        client_id = '2853407314226899'
        client_secret = 'WNnSSSlugQTeFB8vqXdFVLQ1ve8sIird'
        redirect_uri = 'https://ceralfa.odoo.com/meli_login/cere'

        try:
            # Hacer la petición POST para obtener el access_token
            response = requests.post(
                'https://api.mercadolibre.com/oauth/token',
                data={
                    'grant_type': 'authorization_code',
                    'client_id': client_id,
                    'client_secret': client_secret,
                    'code': code,
                    'redirect_uri': redirect_uri,
                },
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )

            result = response.json()

            if response.status_code == 200:
                access_token = result.get('access_token')
                _logger.info(f"Token de acceso obtenido: {access_token}")
                return f"Autenticación exitosa. Token: {access_token}"
            else:
                _logger.error(f"Error en autenticación: {result}")
                return f"Error al obtener el token: {result}"

        except Exception as e:
            _logger.exception("Excepción al obtener el token de acceso")
            return f"Excepción: {str(e)}"
        
    @http.route('/meli_login/primor', type='http', auth='public', website=True)
    def meli_login_primor_callback(self, **kwargs):
        code = kwargs.get('code')
        if not code:
            return "No se recibió el código de autorización"

        _logger.info(f"Recibido código de autorización: {code}")

        # Aquí podrías buscar el client_id y client_secret desde la config o db
        client_id = '4917263316329378'
        client_secret = '2RX1zFOD5Y1QyHEE4QtrumvxsYFY5hKk'
        redirect_uri = 'https://ceralfa.odoo.com/meli_login/primor'

        try:
            # Hacer la petición POST para obtener el access_token
            response = requests.post(
                'https://api.mercadolibre.com/oauth/token',
                data={
                    'grant_type': 'authorization_code',
                    'client_id': client_id,
                    'client_secret': client_secret,
                    'code': code,
                    'redirect_uri': redirect_uri,
                },
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )

            result = response.json()

            if response.status_code == 200:
                access_token = result.get('access_token')
                _logger.info(f"Token de acceso obtenido: {access_token}")
                return f"Autenticación exitosa. Token: {access_token}"
            else:
                _logger.error(f"Error en autenticación: {result}")
                return f"Error al obtener el token: {result}"

        except Exception as e:
            _logger.exception("Excepción al obtener el token de acceso")
            return f"Excepción: {str(e)}"

    @http.route('/meli/notificationer', type='json', auth='none', methods=['POST'], csrf=False)
    def webhook_meli_order(self, **post):
        try:
            data = request.get_json_data()
            _logger.info(f"[WEBHOOK] Notificación recibida: {json.dumps(data)}")

            if not data.get('resource') or not data.get('user_id') or not data.get('topic'):
                _logger.warning("[WEBHOOK] Payload incompleto: %s", data)
                return {"status": "invalid", "message": "Datos incompletos"}

            resource = data['resource']
            event_type = data['topic']  # ← Aquí se usa correctamente el tipo real de evento
            user_id = data['user_id']
            meli_id = resource.split('/')[-1]

            # Buscar la instancia relacionada
            Instance = request.env['vex.instance'].sudo()
            instance = Instance.search([('meli_user_id', '=', str(user_id))], limit=1)
            if not instance:
                _logger.error(f"[WEBHOOK] No se encontró instancia con user_id: {user_id}")
                return {"status": "error", "message": "Instancia no encontrada"}

            Queue = request.env['vex.webhook.queue'].sudo()
            if Queue.search([('meli_id', '=', meli_id), ('event_type', '=', event_type), ('instance_id', '=', instance.id)], limit=1):
                _logger.info(f"[WEBHOOK] Evento ya en cola: {meli_id} - {event_type}")
                return {"status": "exists"}
            if event_type == 'items_prices':
                meli_item_id = resource.split('/')[-2]
                product_id = request.env['product.template'].sudo().search([('meli_product_id', '=', meli_item_id)], limit=1)
                product_id.action_get_price()
            else:
                Queue.create({
                    'meli_id': meli_id,
                    'event_type': event_type,  # ← Se guarda el tipo real, como 'item', 'order', etc.
                    'instance_id': instance.id,
                    'payload': json.dumps(data),
                    'status': 'pending',
                    'processed': False,
                })
            _logger.info(f"[WEBHOOK] Evento {meli_id} ({event_type}) encolado correctamente.")
            return {"status": "success", "message": "Evento encolado"}

        except Exception as e:
            _logger.exception("[WEBHOOK] Error procesando notificación: %s", e)
            return {"status": "error", "message": str(e)}
        
        