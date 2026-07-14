/**
 * Chile B2C - Deja el precio como "$ XXX.XXX (IVA Incl.)" unicamente.
 *
 * IMPORTANTE: a diferencia de la version anterior, este script:
 *  - Solo corre en el sitio B2C (window.CHILE_B2C, seteado por
 *    website_layout_chile.xml segun el NOMBRE del sitio, no un ID fijo).
 *  - No usa MutationObserver sobre document.body: eso competia con el
 *    widget nativo de variantes de Odoo y lo hacia caer al <select> plano.
 *  - No modifica los badges de atributos (.variant_attribute .badge) ni
 *    nada dentro de ul.js_add_cart_variants: eso lo deja intacto el
 *    widget nativo de Odoo. Esta funcion solo toca .product_price
 *    h3.css_editable_mode_hidden, que es una rama del DOM completamente
 *    separada del selector de variantes.
 *  - Se engancha al evento 'change_combination' que el propio Odoo
 *    dispara cuando termina de recalcular una combinacion/variante -
 *    es el punto de extension oficial, no una carrera de renders.
 *
 * Confirmado con el HTML real (Odoo 16 core, website_sale) que el
 * bloque de precio visible al visitante es:
 *   <h3 class="css_editable_mode_hidden">
 *     <span class="oe_price">...</span>
 *     <span class="h6 text-muted">IVA excluido</span>
 *     + IVA                                  <-- texto suelto, sin tag
 *   </h3>
 * El "+ IVA" es un nodo de texto sin envoltorio, por eso no se puede
 * ocultar solo con CSS - se limpia aqui.
 */
(function () {
    'use strict';

    function fixPriceDisplay() {
        if (!window.CHILE_B2C) {
            return;
        }
        document.body.classList.add('chile-b2c-site');

        document.querySelectorAll('.product_price h3.css_editable_mode_hidden').forEach(function (h3) {
            // 1) Agregar el sufijo "(IVA Incl.)" junto al precio principal.
            var priceEl = h3.querySelector('.oe_price');
            if (priceEl && !priceEl.dataset.ivaLabelAdded) {
                var label = document.createElement('small');
                label.className = 'text-muted ms-2 iva-incl-label';
                label.textContent = '(IVA Incl.)';
                priceEl.appendChild(label);
                priceEl.dataset.ivaLabelAdded = '1';
            }

            // 2) Ocultar el "IVA excluido" nativo (span.h6.text-muted).
            h3.querySelectorAll('span.h6.text-muted').forEach(function (span) {
                span.style.display = 'none';
            });

            // 3) Quitar el texto suelto "+ IVA" (nodo de texto directo del h3).
            Array.prototype.forEach.call(h3.childNodes, function (node) {
                if (node.nodeType === Node.TEXT_NODE && node.textContent.trim().indexOf('+') === 0) {
                    node.textContent = '';
                }
            });
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', fixPriceDisplay);
    } else {
        fixPriceDisplay();
    }

    // Hook oficial de Odoo (jQuery custom event, por eso se escucha con $).
    if (window.$) {
        window.$(document).on('change_combination', fixPriceDisplay);
    }
})();
