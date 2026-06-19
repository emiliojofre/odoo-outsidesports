/** @odoo-module **/
/**
 * addval_website_chile - checkout_chile.js
 */

document.addEventListener('DOMContentLoaded', function () {

    const STORAGE_KEY = 'outside_checkout_state';

    // ── Restaurar valores guardados si hay error de validación ────────────────
    // La página de error tiene el mensaje de error visible
    const hasError = document.querySelector('.alert-danger, .o_website_sale_alert, [class*="error"]');
    const saved = sessionStorage.getItem(STORAGE_KEY);

    if (saved) {
        try {
            const data = JSON.parse(saved);

            // Restaurar teléfono en el display
            const phoneDisplay = document.getElementById('phone_display');
            const phoneHidden  = document.getElementById('phone_input');
            if (phoneDisplay && data.phone) {
                phoneDisplay.value = data.phone.replace('+56', '');
                if (phoneHidden) phoneHidden.value = data.phone;
            }

            // Restaurar región
            const stateSelect = document.getElementById('state_id');
            if (stateSelect && data.state_id) {
                stateSelect.value = data.state_id;
                // Disparar change para que Odoo cargue las comunas via AJAX
                stateSelect.dispatchEvent(new Event('change', { bubbles: true }));

                // Restaurar comuna después de que el AJAX cargue las opciones
                if (data.city_id) {
                    const restoreCity = (attempts) => {
                        const citySelect = document.getElementById('city_id_select');
                        if (!citySelect) return;
                        // Intentar seleccionar
                        citySelect.value = data.city_id;
                        if (citySelect.value === data.city_id) {
                            // Éxito: sincronizar el hidden city
                            const cityInput = document.getElementById('city_input');
                            if (cityInput) {
                                const opt = citySelect.options[citySelect.selectedIndex];
                                cityInput.value = opt ? opt.text : '';
                            }
                        } else if (attempts > 0) {
                            // Las opciones aún no cargaron, reintentar
                            setTimeout(() => restoreCity(attempts - 1), 300);
                        }
                    };
                    setTimeout(() => restoreCity(10), 400);
                }
            }

            // Limpiar storage solo si no hay error (es decir, si el submit fue exitoso)
            // Si hay error, mantenemos para el próximo intento
            if (!hasError) {
                sessionStorage.removeItem(STORAGE_KEY);
            }
        } catch(e) {
            sessionStorage.removeItem(STORAGE_KEY);
        }
    }

    // ── Guardar estado antes del submit ───────────────────────────────────────
    const form = document.querySelector('form.checkout_autoformat');
    if (form) {
        form.addEventListener('submit', function () {
            const phoneDisplay = document.getElementById('phone_display');
            const stateSelect  = document.getElementById('state_id');
            const citySelect   = document.getElementById('city_id_select');

            const data = {
                phone:    phoneDisplay ? ('+56' + phoneDisplay.value.trim().replace(/\D/g,'').slice(0,9)) : '',
                state_id: stateSelect  ? stateSelect.value : '',
                city_id:  citySelect   ? citySelect.value  : '',
            };
            sessionStorage.setItem(STORAGE_KEY, JSON.stringify(data));
        }, true);
    }

    // ── Teléfono: sincronizar display → hidden con +56 ────────────────────────
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

        // Al cargar: mostrar sin +56 en el display
        if (phoneHidden.value) {
            phoneDisplay.value = phoneHidden.value.replace('+56', '');
        }
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

    // ── Sincronizar city_input hidden al cambiar comuna ───────────────────────
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
