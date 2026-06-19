# -*- coding: utf-8 -*-
import logging
import re

from odoo import _
from odoo.addons.addval_website_address.controllers.main import WebsiteSaleAddressInfo
from odoo.http import request

_logger = logging.getLogger(__name__)

B2C_WEBSITE_NAME = 'OUTSIDE SPORTS B2C'


def _is_b2c():
    """Retorna True si la request actual es del sitio B2C."""
    return request.website.name == B2C_WEBSITE_NAME


def _validar_rut(rut_raw):
    """
    Valida RUT chileno con algoritmo módulo 11.
    Acepta: 12345678-9, 123456789, 12.345.678-9
    Retorna (bool, rut_normalizado)
    """
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
    """
    Normaliza teléfono chileno a +56XXXXXXXXX.
    Acepta: 9XXXXXXXX (9 dígitos), 569XXXXXXXX (11), +569XXXXXXXX (12)
    """
    phone = phone_raw.strip().replace(' ', '').replace('-', '')
    if re.match(r'^\+56\d{9}$', phone):
        return phone
    if re.match(r'^56\d{9}$', phone):
        return '+' + phone
    if re.match(r'^\d{9}$', phone):
        return '+56' + phone
    return phone_raw.strip()


class WebsiteSaleChile(WebsiteSaleAddressInfo):

    PHONE_PATTERN = re.compile(r'^\+56\d{9}$')

    def _get_country_related_render_values(self, kw, render_values):
        """
        Solo en B2C: filtra country_state_cities por state_id del POST
        para preservar la comuna seleccionada al re-renderizar tras error.
        """
        res = super()._get_country_related_render_values(kw, render_values)

        if not _is_b2c():
            return res

        values = render_values.get('checkout', kw)
        state_id_raw = values.get('state_id', '')
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

        res.update({
            'country_state_cities': cities,
            'state': state,
        })
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

        # Normalizar teléfono
        phone_raw = (address_values.get('phone') or '').strip()
        if phone_raw:
            address_values['phone'] = _normalizar_telefono(phone_raw)

        # Normalizar RUT
        vat_raw = (address_values.get('vat') or '').strip()
        if vat_raw:
            valido, vat_norm = _validar_rut(vat_raw)
            address_values['vat'] = vat_norm if valido else vat_raw

        invalid_fields, missing_fields, error_messages = super()._validate_address_values(
            address_values, partner_sudo, address_type,
            use_delivery_as_billing, required_fields, **kwargs,
        )

        # Validar teléfono normalizado
        phone = (address_values.get('phone') or '').strip()
        if phone and not self.PHONE_PATTERN.fullmatch(phone):
            invalid_fields.add('phone')
            msg = _("Teléfono inválido. Ingresa 9 dígitos, ej: 912345678.")
            if msg not in error_messages:
                error_messages.append(msg)

        # Validar RUT obligatorio y correcto en billing
        if address_type == 'billing':
            vat = (address_values.get('vat') or '').strip()
            if not vat:
                missing_fields.add('vat')
                error_messages.append(_("El RUT es obligatorio."))
            else:
                valido, _ = _validar_rut(vat)
                if not valido:
                    invalid_fields.add('vat')
                    msg = _("RUT inválido. Verifica el dígito verificador. Ej: 12345678-9")
                    if msg not in error_messages:
                        error_messages.append(msg)

        return invalid_fields, missing_fields, error_messages

    def checkout_form_validate(self, mode, all_form_values, data):
        if not _is_b2c():
            return super().checkout_form_validate(mode, all_form_values, data)

        # Normalizar teléfono
        phone_raw = (all_form_values.get('phone') or '').strip()
        if phone_raw:
            norm = _normalizar_telefono(phone_raw)
            all_form_values['phone'] = norm
            if data and 'phone' in data:
                data['phone'] = norm

        error, error_message = super().checkout_form_validate(mode, all_form_values, data)

        # Validar RUT en billing
        if mode[1] == 'billing':
            vat = (all_form_values.get('vat') or '').strip()
            if not vat:
                error['vat'] = 'error'
                msg = _("El RUT es obligatorio.")
                if msg not in error_message:
                    error_message.append(msg)
            else:
                valido, _ = _validar_rut(vat)
                if not valido:
                    error['vat'] = 'error'
                    msg = _("RUT inválido. Verifica el dígito verificador. Ej: 12345678-9")
                    if msg not in error_message:
                        error_message.append(msg)

        return error, error_message
