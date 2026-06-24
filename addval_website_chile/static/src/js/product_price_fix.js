/**
 * Script simple - Limpia estilos display:none en elementos de precio
 */

(function() {
    'use strict';
    
    console.log('[PriceFix] Iniciado');

    function cleanPriceStyles() {
        // Remover display:none de elementos de precio
        const priceElements = document.querySelectorAll('[itemprop="price"], [itemprop="priceCurrency"]');
        
        priceElements.forEach(function(el) {
            if (el.style.display === 'none') {
                el.style.display = '';
            }
        });
        
        console.log('[PriceFix] Limpiados');
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', cleanPriceStyles);
    } else {
        cleanPriceStyles();
    }

})();
