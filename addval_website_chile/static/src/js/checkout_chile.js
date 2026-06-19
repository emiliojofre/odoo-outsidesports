/** @odoo-module **/
/**
 * addval_website_chile - checkout_chile.js
 * Auto-normalización de teléfono y RUT en el formulario de checkout.
 */

document.addEventListener('DOMContentLoaded', function () {

    // ── Teléfono ──────────────────────────────────────────────────────────────
    const phoneInput = document.getElementById('phone_input');
    if (phoneInput) {
        phoneInput.addEventListener('blur', function () {
            let val = phoneInput.value.trim().replace(/[\s\-]/g, '');
            if (!val) return;

            if (val.startsWith('+56') && val.length === 12) {
                // ya correcto
            } else if (/^56\d{9}$/.test(val)) {
                val = '+' + val;
            } else if (/^9\d{8}$/.test(val)) {
                val = '+56' + val;
            } else if (/^\d{9}$/.test(val)) {
                val = '+56' + val;
            }
            phoneInput.value = val;
        });
    }

    // ── RUT ───────────────────────────────────────────────────────────────────
    const vatInput = document.getElementById('vat_input');
    if (vatInput) {
        vatInput.addEventListener('blur', function () {
            let val = vatInput.value.trim().replace(/\./g, '').toUpperCase();
            if (!val) return;

            // Si no tiene guion y tiene al menos 2 chars, insertar guion antes del DV
            if (!val.includes('-') && val.length >= 2) {
                const dv = val.slice(-1);
                const num = val.slice(0, -1);
                val = num + '-' + dv;
            }
            vatInput.value = val;

            // Validación visual cliente (módulo 11)
            const partes = val.split('-');
            if (partes.length === 2) {
                const numStr = partes[0];
                const dvIngresado = partes[1];
                if (/^\d+$/.test(numStr)) {
                    let suma = 0;
                    let mult = 2;
                    for (let i = numStr.length - 1; i >= 0; i--) {
                        suma += parseInt(numStr[i]) * mult;
                        mult = mult < 7 ? mult + 1 : 2;
                    }
                    const resto = 11 - (suma % 11);
                    let dvEsperado = resto === 11 ? '0' : resto === 10 ? 'K' : String(resto);

                    if (dvIngresado !== dvEsperado) {
                        vatInput.classList.add('is-invalid');
                        // Mostrar hint si existe
                        let hint = vatInput.parentElement.querySelector('.rut-hint');
                        if (!hint) {
                            hint = document.createElement('div');
                            hint.className = 'invalid-feedback rut-hint';
                            vatInput.parentElement.appendChild(hint);
                        }
                        hint.textContent = 'RUT inválido. Verifica el dígito verificador.';
                        hint.style.display = 'block';
                    } else {
                        vatInput.classList.remove('is-invalid');
                        vatInput.classList.add('is-valid');
                        const hint = vatInput.parentElement.querySelector('.rut-hint');
                        if (hint) hint.style.display = 'none';
                    }
                }
            }
        });
    }
});
