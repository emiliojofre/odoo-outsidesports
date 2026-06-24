/**
 * Script: Reemplaza el número neto por el del PVP en el h3 de precio
 * y oculta el span "+ IVA"
 */

(function() {
    'use strict';
    
    console.log('[PriceFix] Iniciado');

    function fixPrice() {
        // 1. Buscar el valor del PVP en la sección de SKU/extra fields
        // El PVP está en un span con clase "pvp" o en texto "PVP: $ 16.900"
        let pvpNumber = null;

        // Buscar en todos los elementos el texto "PVP" con un número
        const allElements = document.querySelectorAll('*');
        allElements.forEach(function(el) {
            if (pvpNumber) return;
            const text = el.textContent.trim();
            // Capturar el número después de "PVP: $" o "PVP $"
            const match = text.match(/PVP\s*:\s*\$\s*([\d.,]+)/);
            if (match && el.children.length <= 3) {
                pvpNumber = match[1];
                console.log('[PriceFix] PVP encontrado: ' + pvpNumber);
            }
        });

        // También buscar en spans con clase pvp
        const pvpSpans = document.querySelectorAll('.pvp, [class*="pvp"]');
        pvpSpans.forEach(function(el) {
            if (pvpNumber) return;
            const text = el.textContent.trim();
            const match = text.match(/([\d.,]+)/);
            if (match) {
                pvpNumber = match[1];
                console.log('[PriceFix] PVP en span.pvp: ' + pvpNumber);
            }
        });

        if (!pvpNumber) {
            console.log('[PriceFix] PVP no encontrado, abortando');
            return;
        }

        // 2. Buscar el span con el precio neto (oe_currency_value dentro del h3)
        const priceH3 = document.querySelector('.product_price h3.css_editable_mode_hidden');
        if (!priceH3) {
            console.log('[PriceFix] h3 de precio no encontrado');
            return;
        }

        const currencyValueSpan = priceH3.querySelector('.oe_currency_value');
        if (currencyValueSpan) {
            // Reemplazar el número neto por el del PVP
            console.log('[PriceFix] Reemplazando ' + currencyValueSpan.textContent + ' por ' + pvpNumber);
            currencyValueSpan.textContent = pvpNumber;
        }

        // 3. Ocultar el span "+ IVA" dentro del h3
        const ivaSpan = priceH3.querySelector('.h6.text-muted');
        if (ivaSpan) {
            ivaSpan.style.display = 'none';
            console.log('[PriceFix] Span + IVA ocultado');
        }

        // 4. Agregar "(IVA Incl.)" al lado del precio
        const oePrice = priceH3.querySelector('.oe_price');
        if (oePrice && !oePrice.querySelector('.iva-incl')) {
            const ivaLabel = document.createElement('small');
            ivaLabel.className = 'text-muted ms-1 iva-incl';
            ivaLabel.textContent = '(IVA Incl.)';
            oePrice.appendChild(ivaLabel);
        }

        console.log('[PriceFix] Precio actualizado correctamente');
    }

    setTimeout(fixPrice, 500);

})();
