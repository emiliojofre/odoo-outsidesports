/** @odoo-module **/
/**
 * addval_website_chile - checkout_chile.js
 * - phone_display: input visible de 9 dígitos → sincroniza phone_input hidden con +56
 * - RUT: auto-guion y validación visual módulo 11
 * - Preserva city_id tras re-render por error de validación
 */

document.addEventListener('DOMContentLoaded', function () {

    // ── Teléfono ──────────────────────────────────────────────────────────────
    const phoneDisplay = document.getElementById('phone_display');
    const phoneHidden  = document.getElementById('phone_input');

    if (phoneDisplay && phoneHidden) {
        // Solo dígitos, máximo 9
        phoneDisplay.addEventListener('input', function () {
            phoneDisplay.value = phoneDisplay.value.replace(/\D/g, '').slice(0, 9);
            syncPhone();
        });

        phoneDisplay.addEventListener('blur', syncPhone);

        function syncPhone() {
            const val = phoneDisplay.value.trim();
            phoneHidden.value = val.length === 9 ? '+56' + val : val;
        }

        // Sincronizar también justo antes del submit
        const form = phoneDisplay.closest('form');
        if (form) {
            form.addEventListener('submit', syncPhone, true);
        }

        // Al cargar: si el hidden ya tiene valor (+56XXXXXXXXX), mostrarlo sin prefijo
        if (phoneHidden.value) {
            phoneDisplay.value = phoneHidden.value.replace('+56', '');
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

    // ── Preservar city_id tras error de validación ────────────────────────────
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
