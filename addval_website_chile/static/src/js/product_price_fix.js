/**
 * Script para mostrar precio CON IVA en sitio B2C Chile
 * Busca el elemento de precio y lo multiplica por 1.19
 */

(function() {
    'use strict';
    
    console.log('[PriceFix] Iniciado - Mostrando precios con IVA');

    function fixPriceDisplay() {
        console.log('[PriceFix] Buscando elementos de precio...');
        
        // Buscar span con itemprop="price" que es donde está el precio neto
        const priceSpans = document.querySelectorAll('span[itemprop="price"]');
        console.log('[PriceFix] Encontrados ' + priceSpans.length + ' elementos de precio');

        priceSpans.forEach(function(span) {
            const text = span.textContent.trim();
            const priceMatch = text.match(/[\d.]+/);
            
            if (priceMatch) {
                const netoPrice = parseFloat(priceMatch[0].replace(/\./g, '').replace(/,/g, '.'));
                const withIVA = Math.round(netoPrice * 1.19);
                const formatted = withIVA.toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.');
                
                console.log('[PriceFix] Neto: ' + netoPrice + ' → IVA: ' + withIVA);
                
                // Reemplazar el contenido del span
                span.textContent = formatted;
                
                // Mostrar el span (remover display:none)
                span.style.display = 'block';
            }
        });

        // También buscar en texto visible "+ IVA" y eliminarlo
        const allElements = document.querySelectorAll('*');
        let removed = 0;

        allElements.forEach(function(el) {
            if (el.textContent.includes('+ IVA') && el.children.length === 0 && el.textContent.length < 100) {
                // Si es solo texto "+ IVA", eliminar
                if (el.textContent.trim() === '+ IVA') {
                    el.parentElement.removeChild(el);
                    removed++;
                }
                // Si tiene "$ XXX + IVA", dejar solo el número
                else if (el.textContent.includes('$')) {
                    el.textContent = el.textContent.replace(/\s*\+\s*IVA/i, '').trim();
                }
            }
        });

        console.log('[PriceFix] Eliminados: ' + removed);
    }

    // Ejecutar múltiples veces
    setTimeout(fixPriceDisplay, 300);
    setTimeout(fixPriceDisplay, 800);
    setTimeout(fixPriceDisplay, 1500);

    console.log('[PriceFix] Listo');

})();
