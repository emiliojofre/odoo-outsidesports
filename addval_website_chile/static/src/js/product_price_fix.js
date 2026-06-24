/**
 * Script B2C Chile - Oculta "+ IVA" y el PVP duplicado de abajo
 * El precio principal (PVP) ya viene del módulo eq_website_default_code
 */

(function() {
    'use strict';
    console.log('[PriceFix] Iniciado');

    function fix() {
        // Ocultar span "+ IVA" dentro del bloque de precio
        document.querySelectorAll('.product_price span.h6, .product_price .h6').forEach(function(el) {
            if (el.textContent.includes('IVA')) {
                el.style.setProperty('display', 'none', 'important');
            }
        });

        // Ocultar el h3 con precio neto (css_editable_mode_hidden)
        document.querySelectorAll('.product_price h3.css_editable_mode_hidden').forEach(function(el) {
            el.style.setProperty('display', 'none', 'important');
        });

        console.log('[PriceFix] Listo');
    }

    setTimeout(fix, 300);

    // Re-ejecutar al cambiar variante
    new MutationObserver(function() {
        setTimeout(fix, 200);
    }).observe(
        document.querySelector('.product_price') || document.body,
        { childList: true, subtree: true }
    );

})();

