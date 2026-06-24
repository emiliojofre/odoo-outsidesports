/**
 * Script para corregir la visualización de precios en ficha de producto
 * y listados de productos para el sitio B2C Chile
 * 
 * IMPORTANTE: Solo muestra el PRECIO CON IVA (PVP), NO el precio neto
 * 
 * Soluciona:
 * 1. Listados: Eliminar "$ XXX + IVA" (neto), mostrar solo "PVP: $ YYY"
 * 2. Ficha con variantes: Eliminar "$ XXX + IVA" (neto), mostrar solo "PVP: $ YYY"
 */

document.addEventListener('DOMContentLoaded', function() {
    // Esperar a que todo esté cargado
    setTimeout(function() {
        fixAllPrices();
        // Ejecutar múltiples veces para asegurar que funciona
        setTimeout(fixAllPrices, 300);
        setTimeout(fixAllPrices, 600);
    }, 500);
});

/**
 * Función principal para corregir todos los precios
 */
function fixAllPrices() {
    console.log('[PriceFix] Ejecutando corrección de precios...');
    
    // Corregir precios en LISTADOS (eliminar el que dice "+ IVA")
    fixProductListPrices();
    
    // Corregir precios en FICHA DE PRODUCTO (eliminar el que dice "+ IVA")
    fixProductDetailPrices();
    
    // Observar cambios posteriores (AJAX, filtros, cambios de variante, etc)
    observeAndFixPrices();
}

/**
 * LISTADOS: Elimina el precio neto que dice "+ IVA" 
 * Mantiene solo el PVP "PVP: $ XXX"
 */
function fixProductListPrices() {
    console.log('[PriceFix] Corrigiendo precios en listados...');
    
    // Buscar todos los contenedores que podrían tener precios
    const priceContainers = document.querySelectorAll(
        '.product_price_group, ' +
        '.product-price-group, ' +
        '[class*="price"], ' +
        'span.price'
    );

    priceContainers.forEach(function(container) {
        // El contenedor típicamente tiene DOS precios:
        // 1. $ XXX.XXX + IVA (neto - a ELIMINAR)
        // 2. PVP: $ YYY.YYY (con IVA - a MANTENER)
        
        const text = container.textContent;
        
        // Si contiene AMBOS tipos de precio
        if (text.includes('+ IVA') && text.includes('PVP')) {
            console.log('[PriceFix] Encontrado precio duplicado en listado:', text.slice(0, 50));
            
            // Extraer el precio que dice "PVP: $ XXX"
            const pvpMatch = text.match(/PVP:\s*\$?\s*([\d.,]+)/);
            
            if (pvpMatch) {
                const pvpValue = pvpMatch[1];
                console.log('[PriceFix] Manteniendo PVP:', pvpValue);
                
                // Reemplazar el contenido con solo el PVP
                container.innerHTML = '';
                
                const priceSpan = document.createElement('span');
                priceSpan.className = 'price';
                priceSpan.innerHTML = 'PVP: $ ' + pvpValue + ' <small class="text-muted">(IVA Incl.)</small>';
                
                container.appendChild(priceSpan);
            }
        }
        // Si solo tiene "+ IVA" sin PVP (precio neto - eliminar completamente)
        else if (text.includes('+ IVA') && !text.includes('PVP')) {
            console.log('[PriceFix] Encontrado precio neto, eliminando:', text.slice(0, 50));
            container.innerHTML = '';
        }
    });
}

/**
 * FICHA DE PRODUCTO: Elimina el precio neto "$ XXX + IVA"
 * Mantiene solo el PVP "PVP: $ YYY"
 */
function fixProductDetailPrices() {
    console.log('[PriceFix] Corrigiendo precios en ficha de producto...');
    
    // En ficha, el precio está típicamente en:
    const priceSelectors = [
        '.o_website_sale_sticky .product-price',
        'div[class*="price"]',
        'span.price',
        '.oe_price',
        '[id*="product_price"]'
    ];

    priceSelectors.forEach(function(selector) {
        const elements = document.querySelectorAll(selector);
        
        elements.forEach(function(el) {
            const text = el.textContent;
            
            // Si contiene ambos precios (neto + IVA)
            if (text.includes('+ IVA') && text.includes('PVP')) {
                console.log('[PriceFix] Encontrado doble precio en ficha:', text.slice(0, 50));
                
                // Extraer el PVP
                const pvpMatch = text.match(/PVP:\s*\$?\s*([\d.,]+)/);
                
                if (pvpMatch) {
                    const pvpValue = pvpMatch[1];
                    console.log('[PriceFix] Manteniendo PVP en ficha:', pvpValue);
                    
                    // Reemplazar el contenido
                    el.innerHTML = '';
                    
                    const priceSpan = document.createElement('span');
                    priceSpan.className = 'price h5';
                    priceSpan.innerHTML = '$ ' + pvpValue + ' <small class="text-muted">(IVA Incl.)</small>';
                    
                    el.appendChild(priceSpan);
                }
            }
            // Si solo contiene "+ IVA" (neto)
            else if (text.includes('+ IVA') && !text.includes('PVP')) {
                console.log('[PriceFix] Eliminando precio neto de ficha:', text.slice(0, 50));
                el.innerHTML = '';
            }
        });
    });
}

/**
 * Observa cambios en el DOM (cambios de variante, AJAX, filtros, etc)
 */
function observeAndFixPrices() {
    const observer = new MutationObserver(function(mutations) {
        let shouldFix = false;
        
        mutations.forEach(function(mutation) {
            const text = mutation.target.textContent || '';
            
            // Si hay cambios que incluyan precios
            if (text.includes('$') || text.includes('PVP') || text.includes('+ IVA')) {
                shouldFix = true;
            }
        });

        if (shouldFix) {
            console.log('[PriceFix] Detectado cambio, re-ejecutando correcciones...');
            setTimeout(function() {
                fixProductListPrices();
                fixProductDetailPrices();
            }, 100);
        }
    });

    // Iniciar observación
    observer.observe(document.body, {
        childList: true,
        subtree: true,
        characterData: true
    });
    
    console.log('[PriceFix] Observer iniciado, monitoreando cambios...');
}

/**
 * Log para debugging
 */
console.log('[PriceFix] Script de corrección de precios cargado');
