/**
 * Script ULTRA SIMPLE:
 * 1. Elimina el precio neto (el que dice "+ IVA")
 * 2. Mueve el PVP a su lugar
 */

(function() {
    'use strict';
    
    console.log('[PriceFix] Iniciado');

    function cleanPrices() {
        console.log('[PriceFix] Eliminando precio neto...');
        
        // Buscar TODOS los elementos que contienen "+ IVA"
        const allElements = document.querySelectorAll('*');
        let removed = 0;

        allElements.forEach(function(el) {
            // Si el texto contiene "+ IVA"
            if (el.textContent.includes('+ IVA') && el.children.length === 0 && el.textContent.length < 100) {
                console.log('[PriceFix] Encontrado: ' + el.textContent.trim().slice(0, 40));
                
                // Eliminar el elemento
                try {
                    el.parentElement.removeChild(el);
                    removed++;
                    console.log('[PriceFix] Eliminado');
                } catch(e) {
                    console.log('[PriceFix] Error al eliminar');
                }
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
