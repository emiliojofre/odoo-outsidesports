/**
 * Script SIMPLE - Solo oculta elementos que contienen "+ IVA"
 * No intenta ser inteligente, solo busca y oculta el patrón "+ IVA"
 */

(function() {
    'use strict';
    
    console.log('[PriceFix] Script iniciado - Ocultando "+ IVA"');

    function hideNetoPrices() {
        console.log('[PriceFix] Buscando elementos con "+ IVA"...');
        
        // Buscar TODOS los elementos del documento
        const allElements = document.querySelectorAll('*');
        let hidden = 0;

        allElements.forEach(function(el) {
            // Solo revisar elementos sin hijos (que contienen solo texto)
            if (el.children.length === 0) {
                const text = el.textContent;
                
                // Si contiene "+ IVA", ocultar completamente
                if (text.includes('+ IVA')) {
                    console.log('[PriceFix] Ocultando: ' + text.trim().slice(0, 50));
                    el.style.display = 'none';
                    hidden++;
                }
            }
        });

        console.log('[PriceFix] Elementos ocultados: ' + hidden);
    }

    // Ejecutar cuando esté listo
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', hideNetoPrices);
    } else {
        hideNetoPrices();
    }

    // Observer para cambios posteriores
    const observer = new MutationObserver(function() {
        hideNetoPrices();
    });

    observer.observe(document.body, {
        childList: true,
        subtree: true
    });

    console.log('[PriceFix] Listo');
})();
