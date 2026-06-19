/** @odoo-module **/
/**
 * addval_website_chile - checkout_chile.js
 * - Teléfono: el usuario ingresa 9 dígitos, se envía +56XXXXXXXXX
 * - RUT: auto-inserción de guion y validación visual módulo 11
 * - Preserva city_id seleccionado al re-renderizar tras error de validación
 */

document.addEventListener('DOMContentLoaded', function () {

    // ── Teléfono ──────────────────────────────────────────────────────────────
    const phoneInput = document.getElementById('phone_input');
    if (phoneInput) {
        // Solo permitir dígitos, máximo 9
        phoneInput.addEventListener('input', function () {
            phoneInput.value = phoneInput.value.replace(/\D/g, '').slice(0, 9);
        });

        const form = phoneInput.closest('form');
        if (form) {
            const phoneHidden = document.createElement('input');
            phoneHidden.type = 'hidden';
            phoneHidden.name = 'phone';
            form.appendChild(phoneHidden);
            phoneInput.removeAttribute('name');

            form.addEventListener('submit', function () {
                const val = phoneInput.value.trim();
                phoneHidden.value = val.length === 9 ? '+56' + val : val;
            }, true);
        }
    }

    // ── RUT ───────────────────────────────────────────────────────────────────
    const vatInput = document.getElementById('vat_input');
    if (vatInput) {
        vatInput.addEventListener('blur', function () {
            let val = vatInput.value.trim().replace(/\./g, '').toUpperCase();
            if (!val) return;
            if (!val.includes('-') && val.length >= 2) {
                val = val.slice(0, -1) + '-' + val.slice(-1);
            }
            vatInput.value = val;

            // Validación visual módulo 11
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
                hint.style.fontSize = '0.85em';
                hint.style.marginTop = '4px';
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

    // ── Preservar city_id tras error de validación ────────────────────────────
    // El select de comunas se recarga vía AJAX al cambiar región.
    // Si el formulario fue re-renderizado por error, el server ya filtró
    // country_state_cities por el state_id correcto, por lo que el select
    // debería tener la opción correcta. Solo necesitamos asegurarnos de
    // que el city_input (hidden) esté sincronizado con lo que está seleccionado.
    const citySelect = document.getElementById('city_id_select');
    const cityInput = document.getElementById('city_input');

    if (citySelect && cityInput) {
        // Si hay una opción seleccionada al cargar (re-render tras error),
        // sincronizar el input hidden inmediatamente
        const selectedOption = citySelect.options[citySelect.selectedIndex];
        if (selectedOption && selectedOption.value) {
            cityInput.value = selectedOption.text;
        }

        // Mantener sincronizado al cambiar
        citySelect.addEventListener('change', function () {
            const opt = citySelect.options[citySelect.selectedIndex];
            cityInput.value = opt ? opt.text : '';
        });
    }
});
