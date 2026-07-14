/** @odoo-module **/

import { WebsiteSale } from 'website_sale.website_sale';

// addval_website_address engancha '_onPhoneInput'/'_onSubmitAddressForm' a
// CUALQUIER input[name="phone"] del sitio, exigiendo 11 digitos (+ opcional).
// Nuestro campo de telefono en Chile B2C usa otro formato (9 digitos, con
// "+56" agregado por el servidor) y ahora TAMBIEN se llama "phone" - por
// eso hereda esa regla ajena sin querer. Se neutraliza SOLO en el sitio
// B2C (via window.CHILE_B2C, mismo flag usado en el resto del modulo);
// en cualquier otro sitio se sigue llamando a _super normalmente, sin
// ningun cambio de comportamiento.
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
});

document.addEventListener('DOMContentLoaded', function () {

    // ── Reimponer región/comuna tras un error de validación ───────────────────
    // addval_website_address (_onChangeCountry/_changeState) reconstruye los
    // <select> de región y comuna vía AJAX SIN preservar el valor elegido
    // (borra las opciones y las rearma sin marcar ninguna "selected"), sin
    // importar si esto ocurre al cargar la pagina o al reaccionar a un
    // cambio de pais. En vez de adivinar CUANDO se dispara ese script,
    // reintentamos aplicar el valor correcto (que el servidor SIEMPRE
    // entrega en checkout['state_id']/checkout['city_id'] tras un error,
    // confirmado en website_sale/controllers/main.py "values = kw") hasta
    // ganarle la carrera, con un limite de intentos para no quedar en loop
    // infinito si esos campos vinieran vacios (primera carga sin error).
    const wantedStateEl = document.getElementById('chile_restore_state_id');
    const wantedCityEl = document.getElementById('chile_restore_city_id');
    const wantedState = wantedStateEl ? wantedStateEl.value : '';
    const wantedCity = wantedCityEl ? wantedCityEl.value : '';

    function applyCity(attemptsLeft) {
        if (!wantedCity) {
            return;
        }
        const citySelect = document.getElementById('city_id_select');
        if (!citySelect) {
            return;
        }
        const hasOption = Array.prototype.some.call(
            citySelect.options, function (o) { return o.value === wantedCity; }
        );
        if (citySelect.value !== wantedCity && hasOption) {
            citySelect.value = wantedCity;
            const cityInput = document.getElementById('city_input');
            if (cityInput) {
                const opt = citySelect.options[citySelect.selectedIndex];
                cityInput.value = opt ? opt.text : '';
            }
        }
        if (citySelect.value !== wantedCity && attemptsLeft > 0) {
            setTimeout(function () { applyCity(attemptsLeft - 1); }, 250);
        }
    }

    function applyState(attemptsLeft) {
        if (!wantedState) {
            return;
        }
        const stateSelect = document.getElementById('state_id');
        if (!stateSelect) {
            return;
        }
        const hasOption = Array.prototype.some.call(
            stateSelect.options, function (o) { return o.value === wantedState; }
        );
        if (stateSelect.value !== wantedState && hasOption) {
            stateSelect.value = wantedState;
            // Dispara el cambio a proposito: eso es lo que hace que
            // addval_website_address repueble el <select> de comuna vía
            // AJAX para esta región - luego reintentamos aplicar la comuna.
            stateSelect.dispatchEvent(new Event('change', { bubbles: true }));
        }
        if (stateSelect.value !== wantedState && attemptsLeft > 0) {
            setTimeout(function () { applyState(attemptsLeft - 1); }, 250);
            return;
        }
        applyCity(16);
    }

    if (wantedState) {
        // Pequeño delay inicial: si el script de pais/region corre en el
        // arranque, le da tiempo a terminar su primera pasada antes de que
        // empecemos a pelear por el valor correcto.
        setTimeout(function () { applyState(16); }, 300);
    }

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
});
