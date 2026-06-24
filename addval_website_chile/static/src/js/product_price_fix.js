/**
 * Script: Reemplaza número neto por PVP en el h3 de precio
 */

(function() {
    'use strict';
    
    console.log('[PriceFix] Iniciado');
    
    let isRunning = false;

    function fixPrice() {
        if (isRunning) return;
        isRunning = true;

        // 1. Buscar el PVP
        let pvpNumber = null;
        document.querySelectorAll('*').forEach(function(el) {
            if (pvpNumber) return;
            const match = el.textContent.trim().match(/PVP\s*:\s*\$\s*([\d.,]+)/);
            if (match && el.children.length <= 3) {
                pvpNumber = match[1];
            }
        });

        if (!pvpNumber) { isRunning = false; return; }
        console.log('[PriceFix] PVP: ' + pvpNumber);

        // 2. Reemplazar el número neto por el PVP
        const priceH3 = document.querySelector('.product_price h3.css_editable_mode_hidden');
        if (priceH3) {
            const currencySpan = priceH3.querySelector('.oe_currency_value');
            if (currencySpan && currencySpan.textContent.trim() !== pvpNumber) {
                currencySpan.textContent = pvpNumber;
                console.log('[PriceFix] Número reemplazado: ' + pvpNumber);
            }

            // 3. Agregar "(IVA Incl.)" si no existe
            const oePrice = priceH3.querySelector('.oe_price');
            if (oePrice && !oePrice.querySelector('.iva-incl')) {
                const label = document.createElement('small');
                label.className = 'text-muted ms-2 iva-incl';
                label.style.fontSize = '0.75rem';
                label.textContent = '(IVA Incl.)';
                oePrice.appendChild(label);
            }
        }

        console.log('[PriceFix] Listo');
        setTimeout(function() { isRunning = false; }, 300);
    }

    setTimeout(fixPrice, 500);

    // Observer solo detecta cambios en el precio
    const observer = new MutationObserver(function(mutations) {
        if (isRunning) return;
        for (let i = 0; i < mutations.length; i++) {
            const t = mutations[i].target;
            if (t.classList && t.classList.contains('oe_currency_value')) {
                console.log('[PriceFix] Variante cambiada');
                setTimeout(fixPrice, 200);
                break;
            }
        }
    });

    observer.observe(document.body, { childList: true, subtree: true, characterData: true });

})();

