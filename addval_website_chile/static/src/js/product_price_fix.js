/**
 * B2C Chile - Obtiene precio tarifa B2C (ID=16), calcula IVA 19%
 * y lo muestra en lugar del precio neto
 */
(function () {
    'use strict';

    const PRICELIST_ID = 16;

    function formatCLP(value) {
        return Math.round(value).toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.');
    }

    function renderPrice(priceIva) {
        // Ocultar el bloque de precio neto
        document.querySelectorAll('.product_price h3.css_editable_mode_hidden').forEach(function (el) {
            el.style.display = 'none';
        });

        // Ocultar PVP de abajo (SKU/PVP extra)
        document.querySelectorAll('.o_product_page_extra_field').forEach(function (el) {
            if (el.textContent.includes('PVP')) {
                el.style.display = 'none';
            }
        });

        // Mostrar precio con IVA si no existe ya
        const priceContainer = document.querySelector('.product_price');
        if (!priceContainer) return;

        if (!priceContainer.querySelector('.b2c-price-iva')) {
            const div = document.createElement('div');
            div.className = 'b2c-price-iva';
            div.innerHTML = '$ ' + formatCLP(priceIva) + ' <small class="text-muted">(IVA Incl.)</small>';
            priceContainer.insertAdjacentElement('afterbegin', div);
        }
    }

    function fetchAndRenderPrice() {
        // Obtener el product_id desde el formulario de la página
        const form = document.querySelector('form[action="/shop/cart/update"]');
        if (!form) return;

        const productId = form.querySelector('input[name="product_id"]');
        if (!productId || !productId.value) return;

        // Llamar a la API de Odoo para obtener el precio con la tarifa B2C
        fetch('/web/dataset/call_kw', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                jsonrpc: '2.0',
                method: 'call',
                params: {
                    model: 'product.pricelist',
                    method: 'get_products_price',
                    args: [[PRICELIST_ID], [parseInt(productId.value)], 1],
                    kwargs: {}
                }
            })
        })
        .then(function (r) { return r.json(); })
        .then(function (data) {
            if (data.result) {
                const priceNeto = data.result[parseInt(productId.value)];
                if (priceNeto) {
                    const priceIva = priceNeto * 1.19;
                    console.log('[PriceFix] Neto:', priceNeto, '→ IVA:', Math.round(priceIva));
                    renderPrice(priceIva);
                }
            }
        })
        .catch(function (e) { console.error('[PriceFix] Error:', e); });
    }

    // Ejecutar al cargar
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', fetchAndRenderPrice);
    } else {
        fetchAndRenderPrice();
    }

    // Re-ejecutar al cambiar variante
    document.addEventListener('change', function (e) {
        if (e.target.closest('.js_product')) {
            setTimeout(function () {
                document.querySelectorAll('.b2c-price-iva').forEach(function (el) { el.remove(); });
                fetchAndRenderPrice();
            }, 500);
        }
    });

})();
