# -*- coding: utf-8 -*-
import logging
import re

from odoo import _
from odoo.addons.addval_website_address.controllers.main import WebsiteSaleAddressInfo
from odoo.http import request

_logger = logging.getLogger(__name__)

# internal_credit_payment.WebsiteCreditPayment reimplementa
# checkout_form_validate/_validate_address_values desde cero sin llamar a
# super(), y NO hereda de nuestra cadena (WebsiteSaleChile ->
# WebsiteSaleAddressInfo -> WebsiteSale), sino directo de WebsiteSale -
# son dos ramas independientes. Confirmado via MRO real en logs: cuando
# Odoo arma la clase final que atiende /shop/address, si termina
# resolviendo checkout_form_validate por esa rama, la nuestra queda
# inalcanzable sin importar el orden de carga de modulos (el 'depends'
# en el manifest no alcanza para esto).
# Solucion: heredar EXPLICITAMENTE de ambas clases nosotros mismos, asi
# controlamos el MRO directamente en vez de depender de como Odoo decida
# fusionar los controladores. Con import protegido por try/except para
# no romper en un ambiente donde internal_credit_payment no este
# instalado (ej. otro cliente).
try:
    from odoo.addons.internal_credit_payment.controllers.main import WebsiteCreditPayment
except ImportError:
    WebsiteCreditPayment = None

_BASES = (
    (WebsiteSaleAddressInfo, WebsiteCreditPayment)
    if WebsiteCreditPayment is not None
    else (WebsiteSaleAddressInfo,)
)

B2C_WEBSITE_NAME = 'OUTSIDE SPORTS B2C'


def _is_b2c():
    return request.website.name == B2C_WEBSITE_NAME


def _validar_rut(rut_raw):
    rut = rut_raw.strip().replace('.', '').replace(' ', '').upper()
    if '-' in rut:
        partes = rut.split('-')
        if len(partes) != 2:
            return False, rut_raw
        num_str, dv = partes[0], partes[1]
    elif len(rut) >= 2:
        num_str, dv = rut[:-1], rut[-1]
    else:
        return False, rut_raw
    if not num_str.isdigit():
        return False, rut_raw
    num = int(num_str)
    if num < 1000000 or num > 99999999:
        return False, rut_raw
    suma = 0
    multiplicador = 2
    for d in reversed(num_str):
        suma += int(d) * multiplicador
        multiplicador = multiplicador + 1 if multiplicador < 7 else 2
    resto = 11 - (suma % 11)
    dv_esperado = '0' if resto == 11 else 'K' if resto == 10 else str(resto)
    if dv != dv_esperado:
        return False, rut_raw
    return True, f"{num_str}-{dv_esperado}"


def _normalizar_telefono(phone_raw):
    phone = phone_raw.strip().replace(' ', '').replace('-', '')
    if re.match(r'^\+56\d{9}$', phone):
        return phone
    if re.match(r'^56\d{9}$', phone):
        return '+' + phone
    if re.match(r'^\d{9}$', phone):
        return '+56' + phone
    return phone_raw.strip()


def _completar_city_desde_city_id(values):
    """
    Odoo exige 'city' (texto plano) como campo obligatorio nativo
    (website_sale/controllers/main.py: _get_mandatory_fields_billing/
    _shipping: req = ["name", "email", "street", "city", "country_id"]).
    Nuestro formulario usa un <select> de comuna (city_id) en vez de un
    input de texto libre, y depender de JS para mantener sincronizado un
    campo "city" oculto es fragil (no se dispara si la opcion se
    selecciona programaticamente, p.ej. al reintentar tras un error).

    En vez de eso, derivamos 'city' server-side directamente desde
    'city_id' aqui, de forma que el campo obligatorio de Odoo siempre
    quede satisfecho sin depender de ningun timing de JS. Muta el dict
    recibido in-place.
    """
    if (values.get('city') or '').strip():
        return
    city_id_raw = (values.get('city_id') or '').strip()
    if not city_id_raw or not city_id_raw.isdigit():
        return
    city_rec = request.env['res.city'].browse(int(city_id_raw))
    if city_rec.exists():
        values['city'] = city_rec.name


_logger.info(
    "CHILE_DEBUG: cargando controllers/main.py de addval_website_chile - "
    "WebsiteSaleChile va a heredar de %r", _BASES,
)


def _obtener_campo(values, key):
    """
    'values' (el 'checkout' que arma website_sale.address()) normalmente
    es un dict (direccion nueva, o el kw crudo tras un error). Pero al
    EDITAR una direccion de facturacion existente o gestionar direcciones
    de envio, Odoo pasa directamente un registro res.partner en su lugar
    - que no tiene .get() como un dict (de ahi el AttributeError real
    visto en produccion: 'res.partner' object has no attribute 'get').
    Esta funcion maneja ambos casos de forma segura.
    """
    if isinstance(values, dict):
        return values.get(key) or ''
    valor = getattr(values, key, False)
    if hasattr(valor, 'id'):
        return valor.id or ''
    return valor or ''


class WebsiteSaleChile(*_BASES):

    PHONE_PATTERN = re.compile(r'^\+56\d{9}$')

    def _get_country_related_render_values(self, kw, render_values):
        res = super()._get_country_related_render_values(kw, render_values)
        if not _is_b2c():
            return res
        values = render_values.get('checkout', kw)
        state_id_raw = _obtener_campo(values, 'state_id') or kw.get('state_id', '')
        state = None
        if state_id_raw and str(state_id_raw).isdigit():
            state = request.env['res.country.state'].browse(int(state_id_raw))
            if not state.exists():
                state = None
        if state:
            cities = request.env['res.city'].search([
                ('code', '!=', False),
                ('state_id', '=', state.id),
            ])
        else:
            cities = request.env['res.city'].search([('code', '!=', False)])
        res.update({'country_state_cities': cities, 'state': state})
        return res

    def _validate_address_values(
        self, address_values, partner_sudo, address_type,
        use_delivery_as_billing, required_fields, **kwargs,
    ):
        if not _is_b2c():
            return super()._validate_address_values(
                address_values, partner_sudo, address_type,
                use_delivery_as_billing, required_fields, **kwargs,
            )
        phone_raw = (address_values.get('phone') or '').strip()
        if phone_raw:
            address_values['phone'] = _normalizar_telefono(phone_raw)
        vat_raw = (address_values.get('vat') or '').strip()
        if vat_raw:
            valido, vat_norm = _validar_rut(vat_raw)
            address_values['vat'] = vat_norm if valido else vat_raw
        _completar_city_desde_city_id(address_values)
        invalid_fields, missing_fields, error_messages = super()._validate_address_values(
            address_values, partner_sudo, address_type,
            use_delivery_as_billing, required_fields, **kwargs,
        )
        phone = (address_values.get('phone') or '').strip()
        if phone and not self.PHONE_PATTERN.fullmatch(phone):
            invalid_fields.add('phone')
            msg = _("Teléfono inválido. Ingresa 9 dígitos, ej: 912345678.")
            if msg not in error_messages:
                error_messages.append(msg)
        if address_type == 'billing':
            vat = (address_values.get('vat') or '').strip()
            if not vat:
                missing_fields.add('vat')
                error_messages.append(_("El RUT es obligatorio."))
            else:
                valido, _rut_norm = _validar_rut(vat)
                if not valido:
                    invalid_fields.add('vat')
                    msg = _("RUT inválido. Verifica el dígito verificador. Ej: 12345678-9")
                    if msg not in error_messages:
                        error_messages.append(msg)
        return invalid_fields, missing_fields, error_messages

    def checkout_form_validate(self, mode, all_form_values, data):
        if not _is_b2c():
            return super().checkout_form_validate(mode, all_form_values, data)
        phone_raw = (all_form_values.get('phone') or '').strip()
        if phone_raw:
            norm = _normalizar_telefono(phone_raw)
            all_form_values['phone'] = norm
            if data and 'phone' in data:
                data['phone'] = norm
        _completar_city_desde_city_id(all_form_values)
        if data is not None and not (data.get('city') or '').strip():
            data['city'] = all_form_values.get('city') or data.get('city')
        error, error_message = super().checkout_form_validate(mode, all_form_values, data)
        if error.get('phone'):
            # addval_website_address valida telefono con su propio formato
            # internacional (11 digitos) y agrega su propio mensaje generico;
            # en Chile B2C el formato es 9 digitos + "+56", asi que
            # reemplazamos ese mensaje por uno acorde.
            msg_generico_addval = _(
                "Teléfono inválido. Debe tener 12 caracteres incluyendo '+' al "
                "inicio, o 11 números sin '+'. Vuelve a ingresarlo."
            )
            if msg_generico_addval in error_message:
                error_message.remove(msg_generico_addval)
            msg_chile = _("Teléfono inválido. Debe tener sólo 9 números. Vuelve a ingresarlo.")
            if msg_chile not in error_message:
                error_message.append(msg_chile)
        if mode[1] == 'billing':
            vat = (all_form_values.get('vat') or '').strip()
            if not vat:
                error['vat'] = 'error'
                msg = _("El RUT es obligatorio.")
                if msg not in error_message:
                    error_message.append(msg)
            else:
                valido, _rut_norm = _validar_rut(vat)
                if not valido:
                    error['vat'] = 'error'
                    msg = _("RUT inválido. Verifica el dígito verificador. Ej: 12345678-9")
                    if msg not in error_message:
                        error_message.append(msg)
        return error, error_message


_logger.info(
    "CHILE_DEBUG: WebsiteSaleChile definida. MRO final = %r",
    [f"{c.__module__}.{c.__name__}" for c in WebsiteSaleChile.__mro__],
)
