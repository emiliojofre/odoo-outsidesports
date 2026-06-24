/**
 * Script: Mueve el PVP al lugar donde estaba el precio neto
 */

(function() {
    'use strict';
    
    console.log('[PriceFix] Iniciado - Moviendo PVP a posición de precio');

    function movePVP() {
        // Buscar el contenedor de precio (donde estaba el neto, ahora vacío)
        const priceContainer = document.querySelector('.product_price');
        if (!priceContainer) {
            console.log('[PriceFix] No se encontró .product_price');
            return;
        }

        // Buscar el elemento que contiene el PVP
        // Basado en el HTML visto: está en la sección de SKU/extra fields
        const allElements = document.querySelectorAll('*');
        let pvpElement = null;
        let pvpValue = '';

        allElements.forEach(function(el) {
            if (el.textContent.includes('PVP:') && el.children.length <= 2 && el.textContent.length < 50) {
                pvpElement = el;
                pvpValue = el.textContent.trim();
                console.log('[PriceFix] PVP encontrado: ' + pvpValue);
            }
        });

        if (!pvpElement) {
            console.log('[PriceFix] PVP no encontrado');
            return;
        }

        // Extraer solo el número del PVP
        const pvpMatch = pvpValue.match(/PVP:\s*\$\s*([\d.,]+)/);
        if (!pvpMatch) {
            console.log('[PriceFix] No se pudo extraer número de PVP');
            return;
        }

        const pvpNumber = pvpMatch[1];
        console.log('[PriceFix] Número PVP: ' + pvpNumber);

        // Crear elemento de precio con el mismo estilo que el original
        const priceDiv = document.createElement('div');
        priceDiv.innerHTML = '<h3 class="mt8 mb8" style="font-size:1.75rem; font-weight:bold;">' +
                             '$ ' + pvpNumber + 
                             ' <small class="text-muted" style="font-size:0.9rem;">(IVA Incl.)</small>' +
                             '</h3>';

        // Insertar al inicio del contenedor de precio
        const h3Hidden = priceContainer.querySelector('h3.css_editable_mode_hidden');
        if (h3Hidden) {
            priceContainer.insertBefore(priceDiv, h3Hidden);
        } else {
            priceContainer.insertAdjacentElement('afterbegin', priceDiv);
        }

        console.log('[PriceFix] PVP movido a posición de precio');
    }

    setTimeout(movePVP, 500);

})();
