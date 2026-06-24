/**
 * Script FINAL:
 * Elimina los spans ocultos (display:none) que contienen precios netos
 */

(function() {
    'use strict';
    
    console.log('[PriceFix] Iniciado');

    function cleanPrices() {
        console.log('[PriceFix] Buscando spans ocultos...');
        
        // Buscar TODOS los spans ocultos
        const hiddenSpans = document.querySelectorAll('span[style*="display:none"]');
        console.log('[PriceFix] Spans ocultos encontrados: ' + hiddenSpans.length);
        
        let removed = 0;

        hiddenSpans.forEach(function(span) {
            const text = span.textContent.trim();
            
            // Si contiene un número (precio) o "IVA"
            if (text.match(/[\d.,]+/) || text.includes('IVA')) {
                console.log('[PriceFix] Eliminando: ' + text.slice(0, 50));
                
                try {
                    span.remove();
                    removed++;
                } catch(e) {
                    console.log('[PriceFix] Error: ' + e);
                }
            }
        });

        // También buscar texto visible "+ IVA"
        const allElements = document.querySelectorAll('*');
        allElements.forEach(function(el) {
            if (el.children.length === 0 && el.textContent.trim() === '+ IVA') {
                console.log('[PriceFix] Eliminando "+ IVA" visible');
                try {
                    el.remove();
                    removed++;
                } catch(e) {}
            }
        });

        console.log('[PriceFix] Total eliminados: ' + removed);
    }

    // Ejecutar cuando esté listo
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', cleanPrices);
    } else {
        cleanPrices();
    }

})();
