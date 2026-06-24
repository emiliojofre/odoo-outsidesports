/**
 * Script para corregir la visualización de precios duplicados en ficha de producto
 * y listados de productos para el sitio B2C Chile
 */

document.addEventListener('DOMContentLoaded', function() {
    fixProductPrices();
});

/**
 * Corrige precios duplicados y PVP redundante en ficha de producto
 */
function fixProductPrices() {
    // En ficha de producto individual
    const productDetailPrice = document.querySelector('.o_website_sale_sticky .product-price');
    if (productDetailPrice) {
        fixProductDetailPrice(productDetailPrice);
    }

    // En listados de productos
    const productItems = document.querySelectorAll('.product-price-group');
    productItems.forEach(function(item) {
        fixProductListPrice(item);
    });

    // Observar cambios dinámicos (para AJAX)
    observePriceChanges();
}

/**
 * Corrige el precio en la ficha de detalle del producto
 * Elimina duplicados y mantiene solo el precio final con IVA
 */
function fixProductDetailPrice(priceElement) {
    const priceSpans = priceElement.querySelectorAll('span.price, span.pvp, .product-price-display');
    
    if (priceSpans.length > 1) {
        // Guardar el último precio (que debería ser el más correcto con IVA)
        const lastPrice = priceSpans[priceSpans.length - 1];
        const priceText = lastPrice.textContent.trim();
        
        // Limpiar y reconstruir
        priceElement.innerHTML = '';
        
        const newSpan = document.createElement('span');
        newSpan.className = 'price h5';
        newSpan.innerHTML = priceText + '<small class="text-muted"> (IVA Incl.)</small>';
        
        priceElement.appendChild(newSpan);
    }

    // Asegurar que dice "(IVA Incl.)" y no aparece PVP duplicado
    const smallTags = priceElement.querySelectorAll('small');
    smallTags.forEach(function(small) {
        if (small.textContent.includes('PVP') && small.textContent.includes('IVA')) {
            // Mantener solo el precio con IVA Incl.
            small.textContent = ' (IVA Incl.)';
        }
    });
}

/**
 * Corrige precios en listados de productos
 * Elimina PVP duplicado y mantiene solo el precio con IVA
 */
function fixProductListPrice(productItem) {
    // Encontrar todos los precios en el elemento
    const priceDisplay = productItem.querySelector('.product-price');
    
    if (!priceDisplay) return;

    // Encontrar spans de precio duplicados
    const priceTexts = priceDisplay.querySelectorAll('span[class*="price"], span.pvp');
    
    if (priceTexts.length > 1) {
        // Obtener el valor numérico más grande (generalmente el PVP)
        let maxPrice = 0;
        let maxPriceElement = null;
        
        priceTexts.forEach(function(el) {
            const text = el.textContent.trim();
            const numberMatch = text.match(/[\d.,]+/);
            if (numberMatch) {
                const num = parseFloat(numberMatch[0].replace(/\./g, '').replace(/,/g, '.'));
                if (num > maxPrice) {
                    maxPrice = num;
                    maxPriceElement = el;
                }
            }
        });

        if (maxPriceElement) {
            // Mantener el precio más alto y eliminar duplicados
            priceDisplay.innerHTML = maxPriceElement.outerHTML + '<small class="text-muted"> (IVA Incl.)</small>';
        }
    }

    // Eliminar cualquier texto "PVP: $" redundante
    const text = priceDisplay.textContent;
    if ((text.match(/PVP/g) || []).length > 1) {
        priceDisplay.textContent = priceDisplay.textContent.replace(/PVP:\s*\$?\s*/g, '').trim();
        const price = priceDisplay.textContent.match(/[\d.,]+/);
        if (price) {
            priceDisplay.innerHTML = '<span class="price h6">$' + price[0] + '</span><small class="text-muted"> (IVA Incl.)</small>';
        }
    }
}

/**
 * Observa cambios en el DOM para aplicar las correcciones cuando hay AJAX
 */
function observePriceChanges() {
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList' || mutation.type === 'textContent') {
                // Aplicar correcciones nuevamente
                const productDetailPrice = document.querySelector('.o_website_sale_sticky .product-price');
                if (productDetailPrice) {
                    fixProductDetailPrice(productDetailPrice);
                }
                
                const productItems = document.querySelectorAll('.product-price-group');
                productItems.forEach(function(item) {
                    fixProductListPrice(item);
                });
            }
        });
    });

    // Configurar observer
    const config = {
        childList: true,
        subtree: true,
        characterData: true,
        attributes: false
    };

    // Observar cambios en el contenedor principal
    const mainContent = document.querySelector('main') || document.querySelector('.container');
    if (mainContent) {
        observer.observe(mainContent, config);
    }
}
