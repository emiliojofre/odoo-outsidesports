/**
 * B2C Chile - Solo ejecuta en el sitio B2C (website_id=3)
 */
(function () {
    'use strict';

    // Solo ejecutar en el sitio B2C
    var websiteId = document.documentElement.dataset.websiteId;
    if (websiteId !== '3') return;

    const IVA = 1.19;

    function formatCLP(value) {
        return Math.round(value).toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.');
    }

    function fixVariantPrices() {
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

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', fixVariantPrices);
    } else {
        fixVariantPrices();
    }

    new MutationObserver(function() {
        fixVariantPrices();
    }).observe(document.body, { childList: true, subtree: true });

})();

