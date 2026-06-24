/**
 * B2C Chile:
 * 1. Aplica IVA (x1.19) a los precios de variantes
 * 2. Oculta PVP de abajo
 * 3. Agrega (IVA Incl.)
 */
(function () {
    'use strict';

    const IVA = 1.19;

    function formatCLP(value) {
        return Math.round(value).toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.');
    }

    function fixVariantPrices() {
        // Corregir precios de variantes (+ $7.563)
        document.querySelectorAll('.js_attribute_value .badge, span[data-price]').forEach(function(el) {
            var price = parseFloat(el.dataset.price || 0);
            if (price && !el.dataset.ivaApplied) {
                var newPrice = Math.round(price * IVA);
                el.dataset.price = newPrice;
                el.dataset.ivaApplied = '1';
            }
        });

        // Corregir texto visible "+ $ 7.563"
        document.querySelectorAll('.variant_attribute .badge').forEach(function(el) {
            var text = el.textContent.trim();
            var match = text.match(/([+-])\s*\$\s*([\d.,]+)/);
            if (match && !el.dataset.ivaFixed) {
                var sign = match[1];
                var num = parseFloat(match[2].replace(/\./g, '').replace(/,/g, '.'));
                var newNum = Math.round(num * IVA);
                el.textContent = sign + ' $ ' + formatCLP(newNum);
                el.dataset.ivaFixed = '1';
            }
        });

        // Ocultar PVP de abajo
        document.querySelectorAll('.o_product_page_extra_field').forEach(function(el) {
            el.style.display = 'none';
        });

        // Agregar (IVA Incl.) si no existe
        document.querySelectorAll('.product_price .oe_price').forEach(function(el) {
            if (!el.querySelector('.iva-incl')) {
                var label = document.createElement('small');
                label.className = 'text-muted ms-2 iva-incl';
                label.textContent = '(IVA Incl.)';
                el.appendChild(label);
            }
        });
    }

    // Ejecutar al cargar
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', fixVariantPrices);
    } else {
        fixVariantPrices();
    }

    // Re-ejecutar cuando Odoo actualiza precios por AJAX
    new MutationObserver(function() {
        fixVariantPrices();
    }).observe(document.body, { childList: true, subtree: true });

})();

