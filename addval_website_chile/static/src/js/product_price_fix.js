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
            
            // Si contiene "+ IVA"
            if (text.includes('+ IVA') && text.length < 100) {
                console.log('[PriceFix] Encontrado "+ IVA": ' + text.trim());
                
                // Buscar el contenedor más cercano (línea completa)
                let toRemove = el;
                let parent = el.parentElement;
                
                // Subir hasta encontrar un contenedor apropiado
                // (que probablemente sea un div/span que contiene la línea de precio)
                while (parent && parent.children.length < 10) {
                    const parentText = parent.textContent;
                    
                    // Si el padre contiene PVP, subir más (es el contenedor de precios)
                    if (parentText.includes('PVP')) {
                        // Ir al elemento hermano o al siguiente
                        if (el.nextElementSibling) {
                            console.log('[PriceFix] Eliminando hermano de: ' + text.trim());
                            el.nextElementSibling.remove();
                            removed++;
                            return;
                        }
                        break;
                    }
                    
                    toRemove = parent;
                    parent = parent.parentElement;
                }
                
                // Eliminar el elemento o su contenedor
                if (toRemove && toRemove.parentElement) {
                    console.log('[PriceFix] Eliminando elemento: ' + text.trim());
                    toRemove.parentElement.removeChild(toRemove);
                    removed++;
                }
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
