/**
 * Script FINAL - Solo elimina elementos que contienen "+ IVA"
 * Sin loops, sin recálculos, muy simple y directo
 */

(function() {
    'use strict';
    
    console.log('[PriceFix] Iniciado');

    function removeNetoLines() {
        console.log('[PriceFix] Buscando filas con "+ IVA" para eliminar');
        
        const allElements = document.querySelectorAll('*');
        let removed = 0;

        allElements.forEach(function(el) {
            const text = el.textContent;
            
            // Si contiene "+ IVA" y es un elemento pequeño (probablemente solo precio)
            if (text.includes('+ IVA') && text.length < 100 && el.children.length === 0) {
                console.log('[PriceFix] Eliminando: ' + text.trim());
                el.parentElement.removeChild(el);
                removed++;
            }
        });

        console.log('[PriceFix] Eliminados: ' + removed);
    }

    // Ejecutar UNA SOLA VEZ cuando cargue
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', removeNetoLines);
    } else {
        removeNetoLines();
    }

})();
