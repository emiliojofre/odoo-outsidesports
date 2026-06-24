/**
 * Script AGRESIVO para corregir precios
 * Busca y reemplaza DIRECTAMENTE en el HTML
 * Elimina "$ XXX + IVA" (neto) y mantiene "PVP: $ YYY" (con IVA)
 */

(function() {
    'use strict';
    
    console.log('[PriceFix] Script iniciado');

    /**
     * Busca todos los nodos de texto que contienen "+ IVA" y los procesa
     */
    function fixPricesInDOM() {
        console.log('[PriceFix] Procesando DOM para eliminar "+ IVA"...');
        
        // Obtener todos los nodos de texto del documento
        const walker = document.createTreeWalker(
            document.body,
            NodeFilter.SHOW_TEXT,
            null,
            false
        );

        let node;
        let count = 0;
        const nodesToProcess = [];

        // Recolectar todos los nodos que contienen "+ IVA"
        while (node = walker.nextNode()) {
            if (node.textContent.includes('+ IVA')) {
                nodesToProcess.push(node);
                console.log('[PriceFix] Encontrado nodo con "+ IVA": ' + node.textContent.slice(0, 50));
                count++;
            }
        }

        console.log('[PriceFix] Total de nodos encontrados: ' + count);

        // Procesar cada nodo
        nodesToProcess.forEach(function(node) {
            const parent = node.parentElement;
            if (!parent) return;

            // Si el padre contiene tanto "+ IVA" como "PVP"
            if (parent.textContent.includes('+ IVA') && parent.textContent.includes('PVP')) {
                console.log('[PriceFix] Procesando elemento con ambos precios');
                replacePriceInElement(parent);
            }
            // Si solo contiene "+ IVA", eliminar el nodo
            else if (node.textContent.includes('+ IVA')) {
                console.log('[PriceFix] Eliminando nodo con solo "+ IVA"');
                removeNetoPriceNode(node);
            }
        });
    }

    /**
     * Reemplaza el contenido de un elemento que tiene PVP y neto
     */
    function replacePriceInElement(element) {
        const html = element.innerHTML;
        const text = element.textContent;

        console.log('[PriceFix] HTML original: ' + html.slice(0, 100));

        // Extraer PVP
        const pvpMatch = text.match(/PVP:\s*\$?\s*([\d.,]+)/i);
        if (!pvpMatch) {
            console.log('[PriceFix] No se encontró PVP en: ' + text.slice(0, 50));
            return;
        }

        const pvpValue = pvpMatch[1];
        console.log('[PriceFix] PVP extraído: ' + pvpValue);

        // Limpiar el elemento y mostrar solo PVP
        element.textContent = '';
        element.innerHTML = '$ ' + pvpValue + ' <small class="text-muted">(IVA Incl.)</small>';

        console.log('[PriceFix] Elemento actualizado con PVP: ' + pvpValue);
    }

    /**
     * Elimina los nodos que solo contienen el precio neto
     */
    function removeNetoPriceNode(node) {
        // Si el nodo contiene solo "+ IVA" (es el neto)
        if (node.textContent.match(/^\s*\$?\s*[\d.,]+\s*\+\s*IVA\s*$/)) {
            const parent = node.parentElement;
            if (parent) {
                parent.textContent = '';
                console.log('[PriceFix] Nodo neto eliminado');
            }
        }
    }

    /**
     * Busca dentro de todos los spans que contengan precio
     */
    function fixPriceSpans() {
        console.log('[PriceFix] Buscando spans con precios...');
        
        const allSpans = document.querySelectorAll('span');
        console.log('[PriceFix] Total de spans encontrados: ' + allSpans.length);

        allSpans.forEach(function(span) {
            const text = span.textContent;

            // Si tiene "+ IVA"
            if (text.includes('+ IVA')) {
                console.log('[PriceFix] Span con "+ IVA": ' + text.slice(0, 50));

                // Obtener el padre (que probablemente contiene el PVP también)
                const parent = span.parentElement;
                if (parent && parent.textContent.includes('PVP')) {
                    // Reemplazar todo el padre
                    const pvpMatch = parent.textContent.match(/PVP:\s*\$?\s*([\d.,]+)/i);
                    if (pvpMatch) {
                        parent.innerHTML = '$ ' + pvpMatch[1] + ' <small class="text-muted">(IVA Incl.)</small>';
                        console.log('[PriceFix] Elemento padre actualizado');
                    }
                } else {
                    // Si solo tiene el neto, eliminar
                    span.textContent = '';
                    console.log('[PriceFix] Span neto eliminado');
                }
            }
        });
    }

    /**
     * Busca dentro de divs que contengan precios
     */
    function fixPriceDivs() {
        console.log('[PriceFix] Buscando divs con precios...');
        
        const allDivs = document.querySelectorAll('div');
        console.log('[PriceFix] Total de divs encontrados: ' + allDivs.length);

        allDivs.forEach(function(div) {
            const text = div.textContent;

            // Si contiene "+ IVA"
            if (text.includes('+ IVA')) {
                console.log('[PriceFix] Div con "+ IVA": ' + text.slice(0, 50));

                // Si también tiene PVP
                if (text.includes('PVP')) {
                    const pvpMatch = text.match(/PVP:\s*\$?\s*([\d.,]+)/i);
                    if (pvpMatch) {
                        div.innerHTML = '$ ' + pvpMatch[1] + ' <small class="text-muted">(IVA Incl.)</small>';
                        console.log('[PriceFix] Div con ambos precios actualizado');
                    }
                }
            }
        });
    }

    /**
     * Ejecutar las correcciones
     */
    function runFix() {
        console.log('[PriceFix] ========================================');
        console.log('[PriceFix] INICIANDO CORRECCIÓN DE PRECIOS');
        console.log('[PriceFix] ========================================');

        fixPricesInDOM();
        fixPriceSpans();
        fixPriceDivs();

        console.log('[PriceFix] ========================================');
        console.log('[PriceFix] CORRECCIÓN COMPLETADA');
        console.log('[PriceFix] ========================================');
    }

    /**
     * Ejecutar cuando el DOM esté listo
     */
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            setTimeout(runFix, 500);
            setTimeout(runFix, 1000);
            setTimeout(runFix, 1500);
        });
    } else {
        setTimeout(runFix, 500);
        setTimeout(runFix, 1000);
        setTimeout(runFix, 1500);
    }

    /**
     * Observer para cambios posteriores (variantes, filtros, etc)
     */
    const observer = new MutationObserver(function(mutations) {
        for (let i = 0; i < mutations.length; i++) {
            const text = mutations[i].target.textContent || '';
            if (text.includes('+ IVA')) {
                console.log('[PriceFix] Detectado cambio en precios, ejecutando corrección...');
                setTimeout(function() {
                    fixPriceSpans();
                    fixPriceDivs();
                }, 100);
                break;
            }
        }
    });

    // Iniciar observer
    observer.observe(document.body, {
        childList: true,
        subtree: true,
        characterData: true
    });

    console.log('[PriceFix] Observer iniciado');
})();
