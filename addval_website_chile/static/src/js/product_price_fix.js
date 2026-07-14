/**
 * Chile B2C - Agrega el sufijo "(IVA Incl.)" junto al precio principal.
 *
 * IMPORTANTE: a diferencia de la version anterior, este script:
 *  - Solo corre en el sitio B2C (window.CHILE_B2C, seteado por
 *    website_layout_chile.xml segun el NOMBRE del sitio, no un ID fijo).
 *  - No usa MutationObserver sobre document.body: eso competia con el
 *    widget nativo de variantes de Odoo y lo hacia caer al <select> plano.
 *  - No modifica los badges de atributos (.variant_attribute .badge):
 *    esos los deja intactos el widget nativo de Odoo.
 *  - Se engancha al evento 'change_combination' que el propio Odoo
 *    dispara cuando termina de recalcular una combinacion/variante -
 *    es el punto de extension oficial, no una carrera de renders.
 */
(function () {
    'use strict';

    function addIvaLabel() {
        if (!window.CHILE_B2C) {
            return;
        }
        document.body.classList.add('chile-b2c-site');
        document.querySelectorAll('.product_price .oe_price').forEach(function (el) {
            if (el.dataset.ivaLabelAdded) {
                return;
            }
            var label = document.createElement('small');
            label.className = 'text-muted ms-2 iva-incl-label';
            label.textContent = '(IVA Incl.)';
            el.appendChild(label);
            el.dataset.ivaLabelAdded = '1';
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', addIvaLabel);
    } else {
        addIvaLabel();
    }

    // Hook oficial de Odoo (jQuery custom event, por eso se escucha con $).
    if (window.$) {
        window.$(document).on('change_combination', addIvaLabel);
    }
})();
