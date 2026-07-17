/** @odoo-module **/

import { WebsiteSale } from 'website_sale.website_sale';

// addval_website_address engancha '_onPhoneInput'/'_onSubmitAddressForm' a
// CUALQUIER input[name="phone"] del sitio, exigiendo 11 digitos (+ opcional).
// Nuestro campo de telefono en Chile B2C usa otro formato (9 digitos, con
// "+56" agregado por el servidor) y ahora TAMBIEN se llama "phone" - por
// eso hereda esa regla ajena sin querer.
//
// Ademas, '_changeState'/'_onChangeCountry' reconstruyen los <select> de
// región y comuna vía AJAX BORRANDO las opciones y rearmandolas sin
// preservar el valor elegido (queda seleccionada la primera opción por
// defecto del navegador) - sea que esto ocurra al cargar la pagina o al
// interactuar con el formulario.
//
// Todo esto se neutraliza/parcha SOLO en el sitio B2C (via window.CHILE_B2C,
// mismo flag usado en el resto del modulo); en cualquier otro sitio se
// sigue llamando a _super normalmente, sin ningun cambio de comportamiento.
function _reaplicarSeleccion(selectEl, valorDeseado, attemptsLeft, alLograrlo) {
    if (!selectEl || !valorDeseado) {
        return;
    }
    const tieneOpcion = Array.prototype.some.call(
        selectEl.options, function (o) { return o.value === valorDeseado; }
    );
    if (selectEl.value !== valorDeseado && tieneOpcion) {
        selectEl.value = valorDeseado;
        if (alLograrlo) {
            alLograrlo();
        }
        return;
    }
    if (selectEl.value !== valorDeseado && attemptsLeft > 0) {
        setTimeout(function () {
            _reaplicarSeleccion(selectEl, valorDeseado, attemptsLeft - 1, alLograrlo);
        }, 200);
    }
}

WebsiteSale.include({
    _onPhoneInput: function (ev) {
        if (window.CHILE_B2C) {
            return;
        }
        return this._super.apply(this, arguments);
    },
    _onSubmitAddressForm: function (ev) {
        if (window.CHILE_B2C) {
            return;
        }
        return this._super.apply(this, arguments);
    },
    _changeState: function () {
        if (!window.CHILE_B2C) {
            return this._super.apply(this, arguments);
        }
        const citySelect = document.getElementById('city_id_select');
        const comunaPrevia = citySelect ? citySelect.value : '';
        const resultado = this._super.apply(this, arguments);
        // _changeState no devuelve promesa propia, pero dispara un RPC
        // async que reconstruye el <select> de comuna. Reintentamos
        // reponer la comuna elegida despues de que ese RPC termine.
        if (comunaPrevia) {
            setTimeout(function () {
                const sel = document.getElementById('city_id_select');
                _reaplicarSeleccion(sel, comunaPrevia, 15, function () {
                    const cityInput = document.getElementById('city_input');
                    if (cityInput && sel) {
                        const opt = sel.options[sel.selectedIndex];
                        cityInput.value = opt ? opt.text : '';
                    }
                });
            }, 250);
        }
        return resultado;
    },
    _onChangeCountry: function (ev) {
        if (!window.CHILE_B2C) {
            return this._super.apply(this, arguments);
        }
        const stateSelect = document.getElementById('state_id');
        const regionPrevia = stateSelect ? stateSelect.value : '';
        const resultado = this._super.apply(this, arguments);
        if (regionPrevia) {
            setTimeout(function () {
                const sel = document.getElementById('state_id');
                _reaplicarSeleccion(sel, regionPrevia, 15, function () {
                    // Al reponer la region, dispara 'change' para que
                    // _changeState (ya parchado arriba) reconstruya y
                    // reponga tambien la comuna correspondiente.
                    sel.dispatchEvent(new Event('change', { bubbles: true }));
                });
            }, 250);
        }
        return resultado;
    },
});

document.addEventListener('DOMContentLoaded', function () {

    // ── Teléfono: solo filtrar a dígitos mientras se escribe (cosmético) ──────
    // El input ya se llama "phone" y se envia directo; el servidor
    // (_normalizar_telefono) agrega el "+56" - no hace falta ningun JS de
    // sincronizacion con un campo oculto.
    const phoneDisplay = document.getElementById('phone_display');
    if (phoneDisplay) {
        phoneDisplay.addEventListener('input', function () {
            phoneDisplay.value = phoneDisplay.value.replace(/\D/g, '').slice(0, 9);
        });
    }

    // ── RUT: auto-guion y validación visual módulo 11 ─────────────────────────
    const vatInput = document.getElementById('vat_input');
    if (vatInput) {
        vatInput.addEventListener('blur', function () {
            let val = vatInput.value.trim().replace(/\./g, '').toUpperCase();
            if (!val) return;
            if (!val.includes('-') && val.length >= 2) {
                val = val.slice(0, -1) + '-' + val.slice(-1);
            }
            vatInput.value = val;

            const partes = val.split('-');
            if (partes.length !== 2) return;
            const numStr = partes[0];
            const dvIngresado = partes[1];
            if (!/^\d+$/.test(numStr)) return;

            let suma = 0, mult = 2;
            for (let i = numStr.length - 1; i >= 0; i--) {
                suma += parseInt(numStr[i]) * mult;
                mult = mult < 7 ? mult + 1 : 2;
            }
            const resto = 11 - (suma % 11);
            const dvEsperado = resto === 11 ? '0' : resto === 10 ? 'K' : String(resto);

            let hint = vatInput.parentElement.querySelector('.rut-hint');
            if (!hint) {
                hint = document.createElement('div');
                hint.className = 'rut-hint';
                hint.style.cssText = 'font-size:0.85em; margin-top:4px;';
                vatInput.parentElement.appendChild(hint);
            }
            if (dvIngresado !== dvEsperado) {
                vatInput.classList.add('is-invalid');
                vatInput.classList.remove('is-valid');
                hint.style.color = '#dc3545';
                hint.textContent = 'RUT inválido. El dígito verificador debería ser ' + dvEsperado + '.';
            } else {
                vatInput.classList.remove('is-invalid');
                vatInput.classList.add('is-valid');
                hint.style.color = '#198754';
                hint.textContent = 'RUT válido ✓';
            }
        });
    }

    // ── Sincronizar city_input hidden ─────────────────────────────────────────
    const citySelect = document.getElementById('city_id_select');
    const cityInput  = document.getElementById('city_input');
    if (citySelect && cityInput) {
        const selectedOpt = citySelect.options[citySelect.selectedIndex];
        if (selectedOpt && selectedOpt.value) {
            cityInput.value = selectedOpt.text;
        }
        citySelect.addEventListener('change', function () {
            const opt = citySelect.options[citySelect.selectedIndex];
            cityInput.value = opt ? opt.text : '';
        });
    }

    // ── Confirmación antes de eliminar una dirección de envío ─────────────────
    document.querySelectorAll('.chile-js-delete-shipping').forEach(function (link) {
        link.addEventListener('click', function (ev) {
            ev.preventDefault();
            ev.stopPropagation();
            if (window.confirm('¿Seguro que quieres eliminar esta dirección de envío?')) {
                const form = link.closest('form.chile-delete-shipping-form');
                if (form) {
                    form.submit();
                }
            }
        });
    });
});
