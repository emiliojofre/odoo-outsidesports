# -*- coding: utf-8 -*-
from datetime import datetime
from .responses import PaymentsResponse, PaymentsCreateResponse
import logging
_logger = logging.getLogger(__name__)
class Payments(object):
    ENDPOINT = '/payment/create'
    def __init__(self, client):
        self.client = client
    def get(self, notification_token):
        response = self.client.make_request('GET', '/payment/getStatus',
                    data={'token': notification_token})
        return PaymentsResponse.from_response(response)
    def get_from_commerce_id(self, data):
        response = self.client.make_request('GET', '/payment/getStatusByCommerceId', data=data)
        return PaymentsResponse.from_response(response)
    def post(self, data):
        if hasattr(data, 'expires_date'):
            if isinstance(data['expires_date'], datetime):
                data['expires_date'] = data['expires_date'].isoformat()
        response = self.client.make_request('POST', self.ENDPOINT, data=data)
        return PaymentsCreateResponse.from_response(response)
    def get_id(self, id):
        endpoint = "{0}/{1}/".format(self.ENDPOINT, id)
        response = self.client.make_request('GET', endpoint)
        return PaymentsResponse.from_response(response)
    def delete(self, id):
        endpoint = "{0}/{1}/".format(self.ENDPOINT, id)
        response = self.client.make_request('DELETE', endpoint)
        return SuccessResponse.from_response(response)
    def post_refunds(self, id, amount=None):
        data = None
        if amount:
            data = { 'amount': amount }
        endpoint = "{0}/{1}/refunds".format(self.ENDPOINT, id)
        response = self.client.make_request('POST', endpoint, data=data)
        return SuccessResponse.from_response(response)
