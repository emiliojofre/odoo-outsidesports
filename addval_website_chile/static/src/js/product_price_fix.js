/**
 * Script CONSERVADOR para eliminar precios netos
 * SOLO elimina elementos que:
 * 1. Son span/div con SOLO "$ XXX.XXX" 
 * 2. Están DIRECTAMENTE debajo de un elemento que dice "PVP:"
 * 3. NO tocamos nada más
 */

(function() {
    'use strict';
    
    console.log('[PriceFix] Iniciado - Script conservador');

    /**
     * Función principal - muy conservadora
     */
    function fixPrices() {
        console.log('[PriceFix] Buscando precios netos...');

        // Buscar SOLO elementos que tienen exactamente este patrón:
        // Un elemento que SOLO contiene "$ XXX.XXX" y nada más
        
        const allSpans = document.querySelectorAll('span, div, p');
        let removed = 0;

        allSpans.forEach(function(el) {
            const text = el.textContent.trim();
            
            // PATRÓN ESPECÍFICO: Solo "$ XXX.XXX" (con puntos o comas)
            // Debe coincidir EXACTAMENTE
            if (text.match(/^\$\s*[\d.,]+\s*$/) && el.children.length === 0) {
                
                // Verificar que el PADRE cercano tiene "PVP:"
                let parent = el.parentElement;
                let hasNearbyPVP = false;
                let depth = 0;

                // Subir máximo 3 niveles en el árbol
                while (parent && depth < 3) {
                    if (parent.textContent.includes('PVP:')) {
                        hasNearbyPVP = true;
                        break;
                    }
                    parent = parent.parentElement;
                    depth++;
                }

                // SOLO si encontramos PVP cercano, este elemento es el neto
                if (hasNearbyPVP) {
                    console.log('[PriceFix] Removiendo precio neto: "' + text + '"');
                    
                    // No ocultamos, ELIMINAMOS del DOM completamente
                    el.remove();
                    removed++;
                }
            }
        });

        console.log('[PriceFix] Elementos removidos: ' + removed);
    }

    /**
     * Ejecutar con delay para dejar que cargue todo
     */
    function init() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', function() {
                console.log('[PriceFix] DOM listo');
                setTimeout(fixPrices, 300);
            });
        } else {
            console.log('[PriceFix] DOM ya estaba listo');
            setTimeout(fixPrices, 300);
        }
    }

    // Iniciar
    init();

    /**
     * Observer MÍNIMO - solo para cambios de variante
     */
    const observer = new MutationObserver(function(mutations) {
        // Muy restrictivo - solo ejecuta si hay cambios de texto importantes
        let shouldFix = false;

        for (let i = 0; i < mutations.length; i++) {
            const mutation = mutations[i];
            
            // Solo si hay cambios en nodos de texto que incluyan $
            if (mutation.type === 'characterData' && mutation.target.textContent.includes('$')) {
                shouldFix = true;
                break;
            }
            
            // O si se agregan nuevos elementos con PVP
            if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                for (let j = 0; j < mutation.addedNodes.length; j++) {
                    const node = mutation.addedNodes[j];
                    if (node.textContent && node.textContent.includes('PVP')) {
                        shouldFix = true;
                        break;
                    }
                }
            }
        }

        if (shouldFix) {
            console.log('[PriceFix] Detectado cambio, ejecutando...');
            setTimeout(fixPrices, 100);
        }
    });

    observer.observe(document.body, {
        childList: true,
        subtree: true,
        characterData: true
    });

    console.log('[PriceFix] Listo');

})();
