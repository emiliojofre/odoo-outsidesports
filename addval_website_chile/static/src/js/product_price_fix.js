/**
 * Script AGRESIVO - Busca "+ IVA" sin importar espacios
 * Ejecuta múltiples veces y con delay para contenido dinámico
 */

(function() {
    'use strict';
    
    console.log('[PriceFix] Iniciado');

    function replaceNetoWithIVA() {
        console.log('[PriceFix] Buscando precios netos...');
        
        const allElements = document.querySelectorAll('span, div, p');
        let replaced = 0;

        allElements.forEach(function(el) {
            const text = el.textContent;
            
            // Patrón FLEXIBLE: "+ IVA" puede estar sin espacios
            // "14.202+ IVA" o "$ 14.202 + IVA" o "$ 14.202+ IVA"
            if (text.match(/[+]\s*IVA/i) && text.length < 200 && el.children.length === 0) {
                console.log('[PriceFix] ENCONTRADO: ' + text.trim().slice(0, 60));
                
                // Extraer el precio: buscar cualquier número antes de "+ IVA"
                // Patrón: opcional $, espacios, números con puntos/comas
                const priceMatch = text.match(/\$?\s*([\d.,]+)\s*[+]\s*IVA/i);
                
                if (priceMatch) {
                    const priceString = priceMatch[1];
                    const neto = parseFloat(priceString.replace(/\./g, '').replace(/,/g, '.'));
                    
                    console.log('[PriceFix] Precio extraído: ' + neto);
                    
                    // Calcular con IVA
                    const conIVA = Math.round(neto * 1.19);
                    const formatted = conIVA.toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.');
                    
                    console.log('[PriceFix] Con IVA: $' + formatted);
                    
                    // Reemplazar completamente el texto
                    el.textContent = '$ ' + formatted + ' (IVA Incl.)';
                    replaced++;
                }
            }
        });

        console.log('[PriceFix] Reemplazados: ' + replaced);
        return replaced;
    }

    // Ejecutar múltiples veces con delay para capturar contenido dinámico
    setTimeout(function() {
        console.log('[PriceFix] Ejecutando (300ms)');
        replaceNetoWithIVA();
    }, 300);

    setTimeout(function() {
        console.log('[PriceFix] Ejecutando (800ms)');
        replaceNetoWithIVA();
    }, 800);

    setTimeout(function() {
        console.log('[PriceFix] Ejecutando (1500ms)');
        replaceNetoWithIVA();
    }, 1500);

})();
