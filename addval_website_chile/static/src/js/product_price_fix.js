/**
 * Script: Reemplaza el número neto por el del PVP en el h3 de precio
 * y oculta el span "+ IVA". Se re-ejecuta al cambiar variante.
 */

(function() {
    'use strict';
    
    console.log('[PriceFix] Iniciado');

    function fixPrice() {
        // 1. Buscar el PVP en la sección de extra fields
        let pvpNumber = null;

        const allElements = document.querySelectorAll('*');
        allElements.forEach(function(el) {
            if (pvpNumber) return;
            const text = el.textContent.trim();
            const match = text.match(/PVP\s*:\s*\$\s*([\d.,]+)/);
            if (match && el.children.length <= 3) {
                pvpNumber = match[1];
            }
        });

        if (!pvpNumber) return;
        console.log('[PriceFix] PVP: ' + pvpNumber);

        // 2. Reemplazar el número en el span oe_currency_value
        const priceH3 = document.querySelector('.product_price h3.css_editable_mode_hidden');
        if (!priceH3) return;

        const currencySpan = priceH3.querySelector('.oe_currency_value');
        if (currencySpan && currencySpan.textContent.trim() !== pvpNumber) {
            currencySpan.textContent = pvpNumber;
            console.log('[PriceFix] Número reemplazado');
        }

        // 3. Ocultar TODOS los elementos con "+ IVA" dentro del h3
        priceH3.querySelectorAll('*').forEach(function(el) {
            if (el.textContent.trim() === '+ IVA' || el.textContent.trim() === '+IVA') {
                el.style.display = 'none';
            }
        });

        // 4. Agregar "(IVA Incl.)" si no existe ya
        const oePrice = priceH3.querySelector('.oe_price');
        if (oePrice && !oePrice.querySelector('.iva-incl')) {
            const ivaLabel = document.createElement('small');
            ivaLabel.className = 'text-muted ms-2 iva-incl';
            ivaLabel.style.fontSize = '0.75rem';
            ivaLabel.textContent = '(IVA Incl.)';
            oePrice.appendChild(ivaLabel);
        }

        console.log('[PriceFix] Listo');
    }

    // Ejecutar al cargar
    setTimeout(fixPrice, 500);

    // Re-ejecutar cuando Odoo actualiza el precio al cambiar variante
    const observer = new MutationObserver(function(mutations) {
        for (let i = 0; i < mutations.length; i++) {
            const target = mutations[i].target;
            // Detectar cambio en el precio
            if (target.classList && (
                target.classList.contains('oe_currency_value') ||
                target.classList.contains('oe_price') ||
                target.classList.contains('css_editable_mode_hidden')
            )) {
                console.log('[PriceFix] Variante cambiada, re-ejecutando...');
                setTimeout(fixPrice, 100);
                break;
            }
        }
    });

    observer.observe(document.body, {
        childList: true,
        subtree: true,
        characterData: true
    });

})();
