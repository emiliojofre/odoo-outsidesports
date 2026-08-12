# -*- coding: utf-8 -*-
import requests
import json
import dateutil.parser
from .errors import ValidationError, AuthorizationError, ServiceError
import logging
_logger = logging.getLogger(__name__)

medios_pago = {
    'Webpay': 1,
    'Servipag': 2,
    'Klap': 3,
    'Onepay': 5,
    'Cryptocompra': 8,
    'Todos los medios': 9,
    'Mach': 15,
    "Transferencias bancarias via Khipu": 22,
    "Chek": 25,
    'Webpay 3C': 130,
    "Webpay 6C": 131,
    "Webpay 12C": 132,
    "RedPay": 150,
}


class BaseResponse(object):
    @classmethod
    def from_response(cls, response):
        # FIX NLH: antes esto era `data = json.loads(response.data.decode())`
        # sin proteccion. Si Flow (o un proxy intermedio) responde con un
        # 504/HTML en vez de JSON, esto explotaba con JSONDecodeError y ese
        # error crudo llegaba hasta el checkout del cliente.
        raw = response.data.decode() if response.data else ''
        try:
            data = json.loads(raw)
        except (ValueError, json.JSONDecodeError):
            _logger.warning(
                u"Flow devolvio una respuesta no-JSON (status %s): %s",
                getattr(response, 'status', '?'), raw[:300]
            )
            raise ServiceError(
                'timeout_or_bad_gateway',
                'Flow no respondio correctamente (status %s). '
                'Intente nuevamente en unos minutos.' % getattr(response, 'status', '?')
            )

        _logger.info("res %s" % data)
        if data.get('token') or data.get('flowOrder'):
            return cls.from_data(data)
        else:
            if data.get('code'):
                raise ValidationError.from_data(data)
            if response.status_code == requests.codes.forbidden:
                err = AuthorizationError.from_data(data)
                raise err
            if response.status_code == requests.codes.service_unavailable:
                raise ServiceError.from_data(data)


class PaymentsResponse(BaseResponse):
    def __init__(self, payment_id, url, simplified_transfer_url,
        transfer_url, app_url, ready_for_terminal, token,
        receiver_id, conciliation_date, subject, amount, currency, status,
        payment_data, body, picture_url, receipt_url, return_url, cancel_url,
        notify_url, notify_api_version, expires_date, attachment_urls, bank,
        bank_id, payer_name, email, personal_identifier,
        bank_account_number, out_of_date_conciliation, transaction_id, custom,
        responsible_user_email, send_reminders, send_email, paymentMethod,
        code, message):
        self._payment_id = payment_id
        self._url = url
        self._simplified_transfer_url = simplified_transfer_url
        self._transfer_url = transfer_url
        self._app_url = app_url
        self._ready_for_terminal = ready_for_terminal
        self._token = token
        self._receiver_id = receiver_id
        self._conciliation_date = conciliation_date
        self._subject = subject
        self._amount = amount
        self._currency = currency
        self._status = status
        self._payment_data = payment_data
        self._body = body
        self._picture_url = picture_url
        self._receipt_url = receipt_url
        self._return_url = return_url
        self._cancel_url = cancel_url
        self._notify_url = notify_url
        self._notify_api_version = notify_api_version
        self._expires_date = expires_date
        self._attachment_urls = attachment_urls
        self._bank = bank
        self._bank_id = bank_id
        self._payer_name = payer_name
        self._email = email
        self._personal_identifier = personal_identifier
        self._bank_account_number = bank_account_number
        self._out_of_date_conciliation = out_of_date_conciliation
        self._transaction_id = transaction_id
        self._custom = custom
        self._responsible_user_email = responsible_user_email
        self._send_reminders = send_reminders
        self._send_email = send_email
        self._paymentMethod = paymentMethod
        self._code = code
        self._message = message

    @classmethod
    def from_data(cls, data):
        payment_data = data.get('paymentData', {})
        payment_method = None
        if payment_data and payment_data.get('media'):
            payment_method = medios_pago[payment_data['media']]

        conciliation_date = None
        if payment_data and payment_data.get('date'):
            conciliation_date = dateutil.parser.parse(payment_data.get('date'))
        expires_date = False

        return cls(data.get('flowOrder'), data.get('url'),
            data.get('simplified_transfer_url'), data.get('transfer_url'),
            data.get('app_url'), data.get('ready_for_terminal'),
            data.get('token'), data.get('receiver_id'),
            conciliation_date, data.get('subject'),
            data.get('amount'), data.get('currency'), data.get('status'),
            data.get('paymentData'), data.get('body'),
            data.get('picture_url'), data.get('receipt_url'),
            data.get('return_url'), data.get('cancel_url'),
            data.get('notify_url'), data.get('notify_api_version'),
            expires_date, data.get('attachment_urls'),
            data.get('bank'), data.get('bank_id'), data.get('payer_name'),
            data.get('email') or data.get('payer'), data.get('personal_identifier'),
            data.get('bank_account_number'),
            data.get('out_of_date_conciliation'), data.get('commerceOrder'),
            data.get('custom'), data.get('responsible_user_email'),
            data.get('send_reminders'), data.get('send_email'),
            data.get('paymentMethod', payment_method),
            data.get('code'),data.get('message'))

    @property
    def payment_id(self):
        return self._payment_id
    @property
    def url(self):
        return self._url
    @property
    def simplified_transfer_url(self):
        return self._simplified_transfer_url
    @property
    def transfer_url(self):
        return self._transfer_url
    @property
    def app_url(self):
        return self._app_url
    @property
    def ready_for_terminal(self):
        return self._ready_for_terminal
    @property
    def token(self):
        return self._token
    @property
    def receiver_id(self):
        return self._receiver_id
    @property
    def conciliation_date(self):
        return self._conciliation_date
    @property
    def subject(self):
        return self._subject
    @property
    def amount(self):
        return self._amount
    @property
    def currency(self):
        return self._currency
    @property
    def status(self):
        return self._status
    @property
    def payment_data(self):
        return self._payment_data
    @property
    def body(self):
        return self._body
    @property
    def picture_url(self):
        return self._picture_url
    @property
    def receipt_url(self):
        return self._receipt_url
    @property
    def return_url(self):
        return self._return_url
    @property
    def cancel_url(self):
        return self._cancel_url
    @property
    def notify_url(self):
        return self._notify_url
    @property
    def notify_api_version(self):
        return self._notify_api_version
    @property
    def expires_date(self):
        return self._expires_date
    @property
    def attachment_urls(self):
        return self._attachment_urls
    @property
    def bank(self):
        return self._bank
    @property
    def bank_id(self):
        return self._bank_id
    @property
    def payer_name(self):
        return self._payer_name
    @property
    def email(self):
        return self._email
    @property
    def personal_identifier(self):
        return self._personal_identifier
    @property
    def bank_account_number(self):
        return self._bank_account_number
    @property
    def out_of_date_conciliation(self):
        return self._out_of_date_conciliation
    @property
    def transaction_id(self):
        return self._transaction_id
    @property
    def custom(self):
        return self._custom
    @property
    def responsible_user_email(self):
        return self._responsible_user_email
    @property
    def send_reminders(self):
        return self._send_reminders
    @property
    def send_email(self):
        return self._send_email
    @property
    def paymentMethod(self):
        return self._paymentMethod
    @property
    def code(self):
        return self._code
    @property
    def message(self):
        return self._message


class PaymentsCreateResponse(BaseResponse):
    def __init__(self, payment_id, url, token, simplified_transfer_url,
        transfer_url, app_url, ready_for_terminal):
        self._payment_id = payment_id
        self._url = url
        self._simplified_transfer_url = simplified_transfer_url
        self._transfer_url = transfer_url
        self._app_url = app_url
        self._ready_for_terminal = ready_for_terminal
        self._token = token

    @classmethod
    def from_data(cls, data):
        return cls(data.get('payment_id'), data.get('url'), data.get('token'),
            data.get('simplified_transfer_url'), data.get('transfer_url'),
            data.get('app_url'), data.get('ready_for_terminal'))

    @property
    def payment_id(self):
        return self._payment_id
    @property
    def url(self):
        return self._url
    @property
    def token(self):
        return self._token
    @property
    def simplified_transfer_url(self):
        return self._simplified_transfer_url
    @property
    def transfer_url(self):
        return self._transfer_url
    @property
    def app_url(self):
        return self._app_url
    @property
    def ready_for_terminal(self):
        return self._ready_for_terminal


class ReceiversCreateResponse(BaseResponse):
    def __init__(self, receiver_id, secret):
        self._receiver_id = receiver_id
        self._secret = secret

    @classmethod
    def from_data(cls, data):
        return cls(data.get('receiver_id'), data.get('secret'))

    @property
    def receiver_id(self):
        return self._receiver_id
    @property
    def secret(self):
        return self._secret


class BanksResponse(BaseResponse):
    def __init__(self, banks):
        self._banks = banks

    @classmethod
    def from_data(cls, data):
        return cls(banks.get('banks'))

    @property
    def banks(self):
        return self._banks


class SuccessResponse(BaseResponse):
    def __init__(self, message):
        self._message = message

    @classmethod
    def from_data(cls, data):
        return cls(data['message'])

    @property
    def message(self):
        return self._message
