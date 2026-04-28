from odoo import http
from odoo.http import request

class AlasxpressController(http.Controller):

    @http.route('/delivery-orders/hook-alas', type='json', auth='public', methods=['POST'], csrf=False)
    def alas_webhook(self):
        data = request.jsonrequest
        order_id = data.get('deliveryOrderId')
        status = data.get('status')
        
        picking = request.env['stock.picking'].sudo().search([('alas_delivery_id', '=', order_id)], limit=1)
        if picking:
            picking.message_post(body=f"<b>Webhook Alasxpress:</b> El estado ha cambiado a <i>{status}</i>")
        return {"status": "success"}