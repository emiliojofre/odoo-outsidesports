/**
 * Script ULTRA AGRESIVO para eliminar precios netos
 * Estrategia: Elimina CUALQUIER elemento de precio que NO contenga "PVP:"
 * Mantiene SOLO los que dicen "PVP: $ XXX"
 */

(function() {
    'use strict';
    
    console.log('[PriceFix] ============ SCRIPT INICIADO ============');

    /**
     * Elimina elementos de precio que no son PVP
     * Busca patterns como:
     * - "$ XXX.XXX" (sin PVP delante)
     * - "$ XXX.XXX + IVA"
     * - Números de precio que no tengan PVP
     */
    function eliminatePriceRows() {
        console.log('[PriceFix] Buscando filas de precio neto a eliminar...');
        
        // Estrategia 1: Buscar TODOS los elementos que contengan SOLO números y $
        // pero que NO tengan "PVP:"
        
        const allElements = document.querySelectorAll('*');
        let eliminados = 0;
        
        allElements.forEach(function(el) {
            // Saltar elementos muy grandes o especiales
            if (el.children.length > 0 && el.textContent.length > 200) {
                return;
            }

            const text = el.textContent.trim();
            
            // Patrón 1: "$ XXX.XXX" (solo número con $, sin PVP)
            // Y que el padre contiene PVP
            if (text.match(/^\s*\$\s*[\d.,]+\s*$/) && el.parentElement) {
                if (el.parentElement.textContent.includes('PVP')) {
                    console.log('[PriceFix] Eliminando precio neto: ' + text);
                    el.style.display = 'none';
                    eliminados++;
                }
            }
            
            // Patrón 2: "$ XXX.XXX + IVA"
            if (text.includes('+ IVA')) {
                console.log('[PriceFix] Eliminando "+ IVA": ' + text);
                el.style.display = 'none';
                eliminados++;
            }
            
            // Patrón 3: Si es un div/span pequeño que SOLO contiene precio sin PVP
            // y hay un PVP en el mismo contenedor padre
            const parentText = el.parentElement ? el.parentElement.textContent : '';
            if (text.match(/^\s*\$\s*[\d.,]+\s*$/) && 
                parentText.includes('PVP') && 
                !text.includes('PVP')) {
                console.log('[PriceFix] Ocultando precio sin PVP: ' + text);
                el.style.display = 'none';
                eliminados++;
            }
        });

        console.log('[PriceFix] Total eliminados: ' + eliminados);
        return eliminados;
    }

    /**
     * Busca contenedores de precio específicos y los limpia
     */
    function cleanPriceContainers() {
        console.log('[PriceFix] Limpiando contenedores de precio...');

        // Buscar spans y divs que contengan precios
        const priceElements = document.querySelectorAll(
            'span, div, p'
        );

        let limpios = 0;

        priceElements.forEach(function(el) {
            const text = el.textContent.trim();
            
            // Si es SOLO un número con $
            if (text.match(/^\s*\$\s*[\d.,]+\s*$/)) {
                const parentText = el.parentElement ? el.parentElement.textContent : '';
                
                // Si el padre tiene PVP pero este elemento NO
                if (parentText.includes('PVP') && !text.includes('PVP')) {
                    console.log('[PriceFix] Limpiando elemento neto: ' + text);
                    el.textContent = '';
                    el.style.display = 'none';
                    limpios++;
                }
            }
            
            // Si contiene "+ IVA"
            if (text.includes('+ IVA')) {
                console.log('[PriceFix] Eliminando elemento con "+ IVA": ' + text);
                el.textContent = '';
                el.style.display = 'none';
                limpios++;
            }
        });

        console.log('[PriceFix] Total limpiados: ' + limpios);
        return limpios;
    }

    /**
     * Busca en filas de productos y elimina segundo precio
     */
    function fixProductRows() {
        console.log('[PriceFix] Procesando filas de productos...');

        // Buscar contenedores de productos
        const productContainers = document.querySelectorAll(
            '.product_item, ' +
            '.product-item, ' +
            '[class*="product"][class*="item"], ' +
            '.oe_product, ' +
            '.product'
        );

        console.log('[PriceFix] Contenedores de producto encontrados: ' + productContainers.length);

        productContainers.forEach(function(container) {
            const allText = container.textContent;
            
            // Contar cuántos precios hay (patrones con $)
            const priceMatches = allText.match(/\$\s*[\d.,]+/g);
            
            if (priceMatches && priceMatches.length > 1) {
                console.log('[PriceFix] Producto con múltiples precios encontrado');
                
                // Buscar todos los elementos dentro que contengan $
                const internalPrices = container.querySelectorAll('*');
                let pvpFound = false;
                
                internalPrices.forEach(function(el) {
                    const text = el.textContent;
                    
                    // Si tiene "PVP:" marcar que ya encontramos el principal
                    if (text.includes('PVP:')) {
                        pvpFound = true;
                    }
                    // Si ya pasamos PVP y encuentra otro precio, eliminar
                    else if (pvpFound && text.match(/^\s*\$\s*[\d.,]+\s*$/) && el.children.length === 0) {
                        console.log('[PriceFix] Eliminando precio duplicado: ' + text);
                        el.style.display = 'none';
                    }
                });
            }
        });
    }

    /**
     * Ejecuta todas las funciones
     */
    function runAllFixes() {
        console.log('[PriceFix] ========== INICIANDO CORRECCIONES ==========');
        
        let total = 0;
        total += eliminatePriceRows();
        total += cleanPriceContainers();
        fixProductRows();
        
        console.log('[PriceFix] ========== CORRECCIONES COMPLETADAS ==========');
        console.log('[PriceFix] Total de elementos procesados: ' + total);
    }

    /**
     * Ejecutar cuando esté listo
     */
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            console.log('[PriceFix] DOMContentLoaded detectado');
            setTimeout(runAllFixes, 300);
            setTimeout(runAllFixes, 800);
            setTimeout(runAllFixes, 1500);
        });
    } else {
        console.log('[PriceFix] DOM ya está listo');
        setTimeout(runAllFixes, 300);
        setTimeout(runAllFixes, 800);
        setTimeout(runAllFixes, 1500);
    }

    /**
     * Observer para cambios dinámicos
     */
    const observer = new MutationObserver(function(mutations) {
        // Buscar si hay cambios relacionados con precios
        let hasPriceChanges = false;
        
        for (let i = 0; i < mutations.length; i++) {
            const text = mutations[i].target.textContent || '';
            if (text.includes('PVP') || text.includes('$')) {
                hasPriceChanges = true;
                break;
            }
        }

        if (hasPriceChanges) {
            console.log('[PriceFix] Detectado cambio de precio, re-ejecutando...');
            setTimeout(function() {
                cleanPriceContainers();
                fixProductRows();
            }, 50);
        }
    });

    observer.observe(document.body, {
        childList: true,
        subtree: true,
        characterData: true
    });

    console.log('[PriceFix] Observer activo');
    console.log('[PriceFix] ============================================');

})();
