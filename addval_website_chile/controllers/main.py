# -*- coding: utf-8 -*-
import logging
import re

from odoo import _
from odoo.addons.addval_website_address.controllers.main import WebsiteSaleAddressInfo

_logger = logging.getLogger(__name__)


def _validar_rut(rut_raw):
    """
    Valida RUT chileno con algoritmo módulo 11.
    Acepta formatos: 12345678-9, 123456789, 12.345.678-9
    Retorna (bool, rut_normalizado)
    """
    # Limpiar puntos y espacios, dejar solo dígitos y K/k y guion
    rut = rut_raw.strip().replace('.', '').replace(' ', '').upper()

    # Si tiene guion separar, si no asumir último char es DV
    if '-' in rut:
        partes = rut.split('-')
        if len(partes) != 2:
            return False, rut_raw
        num_str, dv = partes[0], partes[1]
    elif len(rut) >= 2:
        num_str = rut[:-1]
        dv = rut[-1]
    else:
        return False, rut_raw

    # Número debe ser solo dígitos
    if not num_str.isdigit():
        return False, rut_raw

    num = int(num_str)
    if num < 1000000 or num > 99999999:
        return False, rut_raw

    # Calcular DV esperado
    suma = 0
    multiplicador = 2
    for d in reversed(num_str):
        suma += int(d) * multiplicador
        multiplicador = multiplicador + 1 if multiplicador < 7 else 2

    resto = 11 - (suma % 11)
    if resto == 11:
        dv_esperado = '0'
    elif resto == 10:
        dv_esperado = 'K'
    else:
        dv_esperado = str(resto)

    if dv != dv_esperado:
        return False, rut_raw

    # Retornar normalizado: XXXXXXXX-D
    return True, f"{num_str}-{dv_esperado}"


def _normalizar_telefono(phone_raw):
    """
    Normaliza teléfono chileno a formato +56XXXXXXXXX (12 chars).
    Acepta: 9XXXXXXXX, 56XXXXXXXXX, +56XXXXXXXXX
    """
    phone = phone_raw.strip().replace(' ', '').replace('-', '')
    if phone.startswith('+56') and len(phone) == 12:
        return phone
    if phone.startswith('56') and len(phone) == 11:
        return '+' + phone
    if re.match(r'^9\d{8}$', phone):
        return '+56' + phone
    if re.match(r'^\d{9}$', phone):
        return '+56' + phone
    return phone_raw.strip()


class WebsiteSaleChile(WebsiteSaleAddressInfo):

    PHONE_PATTERN = re.compile(r'^\+56\d{9}$')

    def _validate_address_values(
        self,
        address_values,
        partner_sudo,
        address_type,
        use_delivery_as_billing,
        required_fields,
        **kwargs,
    ):
        # Normalizar teléfono antes de validar
        phone_raw = (address_values.get('phone') or '').strip()
        if phone_raw:
            address_values['phone'] = _normalizar_telefono(phone_raw)

        # Normalizar y validar RUT
        vat_raw = (address_values.get('vat') or '').strip()
        if vat_raw:
            valido, vat_normalizado = _validar_rut(vat_raw)
            if valido:
                address_values['vat'] = vat_normalizado
            else:
                address_values['vat'] = vat_raw

        invalid_fields, missing_fields, error_messages = super()._validate_address_values(
            address_values,
            partner_sudo,
            address_type,
            use_delivery_as_billing,
            required_fields,
            **kwargs,
        )

        # Validar formato teléfono ya normalizado
        phone = (address_values.get('phone') or '').strip()
        if phone and not self.PHONE_PATTERN.fullmatch(phone):
            invalid_fields.add('phone')
            if _('Teléfono inválido') not in ' '.join(error_messages):
                error_messages.append(_(
                    "Teléfono inválido. Ingresa tu número chileno, ej: +56912345678 o 912345678."
                ))

        # Validar RUT obligatorio y correcto
        vat = (address_values.get('vat') or '').strip()
        if address_type == 'billing':
            if not vat:
                missing_fields.add('vat')
                error_messages.append(_("El RUT es obligatorio."))
            else:
                valido, _ = _validar_rut(vat)
                if not valido:
                    invalid_fields.add('vat')
                    error_messages.append(_(
                        "RUT inválido. Verifica el número y dígito verificador. Ej: 12345678-9"
                    ))

        return invalid_fields, missing_fields, error_messages

    def checkout_form_validate(self, mode, all_form_values, data):
        # Normalizar teléfono antes de pasar al padre
        phone_raw = (all_form_values.get('phone') or '').strip()
        if phone_raw:
            all_form_values['phone'] = _normalizar_telefono(phone_raw)
            if data and 'phone' in data:
                data['phone'] = all_form_values['phone']

        error, error_message = super().checkout_form_validate(mode, all_form_values, data)

        # Validar RUT
        vat = (all_form_values.get('vat') or '').strip()
        if mode[1] == 'billing':
            if not vat:
                error['vat'] = 'error'
                msg = _("El RUT es obligatorio.")
                if msg not in error_message:
                    error_message.append(msg)
            else:
                valido, vat_norm = _validar_rut(vat)
                if not valido:
                    error['vat'] = 'error'
                    msg = _("RUT inválido. Verifica el número y dígito verificador. Ej: 12345678-9")
                    if msg not in error_message:
                        error_message.append(msg)

        return error, error_message
