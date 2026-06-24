/**
 * Script para corregir la visualización de precios en ficha de producto
 * y listados de productos para el sitio B2C Chile
 * 
 * IMPORTANTE: Solo mostra el PRECIO CON IVA (PVP), NO el precio neto
 * 
 * Soluciona:
 * 1. Imagen 1: Eliminar el precio neto ($14.202), mostrar solo PVP ($16.900)
 * 2. Imagen 2: Mostrar un solo precio sin repeticiones, eliminar duplicados
 */

document.addEventListener('DOMContentLoaded', function() {
    // Esperar a que todo esté cargado
    setTimeout(fixAllPrices, 500);
});

/**
 * Función principal para corregir todos los precios
 */
function fixAllPrices() {
    // Corregir precios en ficha de producto individual
    fixProductDetailPrices();
    
    // Corregir precios en listados
    fixProductListPrices();
    
    // Observar cambios posteriores (AJAX, filtros, etc)
    observeAndFixPrices();
}

/**
 * Corrige precios en la ficha detallada del producto (imagen 1)
 * OBJETIVO: Mostrar SOLO el precio con IVA, eliminar el neto
 */
function fixProductDetailPrices() {
    // Buscar el contenedor principal de precios
    const priceContainers = document.querySelectorAll(
        '.o_website_sale_sticky .product-price, ' +
        '.product-price-container, ' +
        'span.price, ' +
        'div[id*="product_price"], ' +
        '.oe_price'
    );

    priceContainers.forEach(function(container) {
        // Obtener todos los elementos que podrían contener precios
        const priceElements = container.querySelectorAll('span, div, p');
        const prices = [];
        
        priceElements.forEach(function(el) {
            const text = el.textContent.trim();
            // Buscar números de precio (ej: $14.202, $16.900)
            if (text.match(/\$?\s*[\d.,]+/) && !text.includes('(IVA')) {
                const numMatch = text.match(/[\d.,]+/);
                if (numMatch) {
                    const numValue = parseFloat(numMatch[0].replace(/\./g, '').replace(/,/g, '.'));
                    prices.push({
                        element: el,
                        text: text,
                        value: numValue,
                        html: el.innerHTML
                    });
                }
            }
        });

        // Si hay múltiples precios, mantener solo el MAYOR (que es el con IVA/PVP)
        if (prices.length > 1) {
            const maxPrice = prices.reduce((max, p) => p.value > max.value ? p : max);
            
            // Limpiar el contenedor
            container.innerHTML = '';
            
            // Recrear con solo el precio máximo (PVP con IVA)
            const priceSpan = document.createElement('span');
            priceSpan.className = 'price h5';
            
            // Formatear el precio correctamente
            const formattedPrice = '$ ' + maxPrice.value.toLocaleString('es-CL');
            priceSpan.innerHTML = formattedPrice + ' <small class="text-muted">(IVA Incl.)</small>';
            
            container.appendChild(priceSpan);
        }
        // Si tiene "PVP:" duplicado, limpiar y dejar solo uno
        else if (container.textContent.includes('PVP')) {
            const pvpMatches = container.textContent.match(/PVP\s*:\s*\$?\s*[\d.,]+/g);
            
            if (pvpMatches && pvpMatches.length > 1) {
                // Usar el último PVP (debería ser el correcto)
                const lastPvp = pvpMatches[pvpMatches.length - 1];
                const priceMatch = lastPvp.match(/[\d.,]+/);
                
                if (priceMatch) {
                    const formattedPrice = '$ ' + parseFloat(priceMatch[0].replace(/\./g, '').replace(/,/g, '.')).toLocaleString('es-CL');
                    
                    container.innerHTML = '';
                    const priceSpan = document.createElement('span');
                    priceSpan.className = 'price h5';
                    priceSpan.innerHTML = formattedPrice + ' <small class="text-muted">(IVA Incl.)</small>';
                    container.appendChild(priceSpan);
                }
            }
        }
    });
}

/**
 * Corrige precios en listados de productos (imagen 2)
 * OBJETIVO: Mostrar SOLO UN precio (el con IVA), sin duplicados
 */
function fixProductListPrices() {
    // Buscar todos los contenedores de precio en listados
    const priceDisplays = document.querySelectorAll(
        '.products_grid .product-price, ' +
        '.product_list .product-price, ' +
        '.product-price-group .product-price, ' +
        '[class*="product"][class*="price"] .product-price'
    );

    priceDisplays.forEach(function(priceDisplay) {
        const text = priceDisplay.textContent.trim();
        const innerHTML = priceDisplay.innerHTML;
        
        // Extraer TODOS los números de precio del contenedor
        const priceMatches = text.match(/[\d.,]+/g);
        
        if (priceMatches && priceMatches.length > 0) {
            // Convertir todos los matches a números y encontrar el mayor (con IVA)
            const prices = priceMatches.map(match => {
                return parseFloat(match.replace(/\./g, '').replace(/,/g, '.'));
            });
            
            const maxPrice = Math.max(...prices);
            
            // Si hay múltiples precios, limpiar y dejar solo el máximo
            if (prices.length > 1 || (text.match(/\$/g) && text.match(/\$/g).length > 1)) {
                priceDisplay.innerHTML = '';
                
                const priceSpan = document.createElement('span');
                priceSpan.className = 'price';
                
                // Formatear el precio máximo (con IVA)
                const formattedPrice = '$ ' + maxPrice.toLocaleString('es-CL');
                priceSpan.innerHTML = formattedPrice + ' <small class="text-muted">(IVA Incl.)</small>';
                
                priceDisplay.appendChild(priceSpan);
            }
            // Si solo hay un precio pero está repetido en el texto
            else if ((text.match(/PVP/g) || []).length > 1) {
                const numValue = parseFloat(priceMatches[0].replace(/\./g, '').replace(/,/g, '.'));
                
                priceDisplay.innerHTML = '';
                const priceSpan = document.createElement('span');
                priceSpan.className = 'price';
                
                const formattedPrice = '$ ' + numValue.toLocaleString('es-CL');
                priceSpan.innerHTML = formattedPrice + ' <small class="text-muted">(IVA Incl.)</small>';
                
                priceDisplay.appendChild(priceSpan);
            }
        }
    });
}

/**
 * Observa cambios en el DOM y aplica las correcciones cuando hay actualizaciones dinámicas
 */
function observeAndFixPrices() {
    const observer = new MutationObserver(function(mutations) {
        let hasPriceChanges = false;
        
        mutations.forEach(function(mutation) {
            // Verificar si los cambios incluyen elementos de precio
            if (mutation.type === 'childList') {
                const addedNodes = Array.from(mutation.addedNodes);
                if (addedNodes.some(node => {
                    if (node.nodeType === 1) { // Element node
                        const className = node.className || '';
                        const text = node.textContent || '';
                        return className.includes('price') || 
                               className.includes('product') ||
                               text.includes('$');
                    }
                    return false;
                })) {
                    hasPriceChanges = true;
                }
            }
        });

        if (hasPriceChanges) {
            setTimeout(fixAllPrices, 100);
        }
    });

    // Iniciar observación en el documento
    observer.observe(document.body, {
        childList: true,
        subtree: true,
        characterData: false,
        attributes: false
    });
}

