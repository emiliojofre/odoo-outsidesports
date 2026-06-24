/**
 * Script para agregar IVA al precio Publico B2C
 * Tarifa: Publico B2C (ID=16)
 * IVA: 19%
 * 
 * Estrategia:
 * 1. Buscar todos los precios de la tarifa Publico B2C
 * 2. Multiplicar por 1.19 (agregar 19% IVA)
 * 3. Mostrar solo ese precio con IVA
 * 4. Eliminar duplicados y confusión
 */

(function() {
    'use strict';
    
    console.log('[PriceFix] Iniciado - Calculando precios con IVA 19%');

    const IVA_RATE = 1.19; // 19% de IVA

    /**
     * Encuentra todos los precios en la página y los ajusta con IVA
     */
    function addIVAToPublicoB2C() {
        console.log('[PriceFix] Buscando precios Publico B2C...');
        
        // Buscar todos los spans/divs que contengan precios
        const allElements = document.querySelectorAll('span, div, p, td');
        let processed = 0;

        allElements.forEach(function(el) {
            const text = el.textContent.trim();
            
            // Patrón: "$ XXX.XXX" o similares
            const priceMatch = text.match(/^\$?\s*([\d.,]+)\s*$/);
            
            if (priceMatch && el.children.length === 0) {
                // Convertir el precio encontrado
                const priceString = priceMatch[1];
                const priceValue = parseFloat(priceString.replace(/\./g, '').replace(/,/g, '.'));
                
                // Calcular precio con IVA
                const priceWithIVA = priceValue * IVA_RATE;
                
                // Verificar si el padre cercano contiene "PVP:" 
                let parent = el.parentElement;
                let hasPVP = false;
                let depth = 0;
                
                while (parent && depth < 3) {
                    if (parent.textContent.includes('PVP:')) {
                        hasPVP = true;
                        break;
                    }
                    parent = parent.parentElement;
                    depth++;
                }
                
                // Si NO tiene PVP cercano, es la tarifa Publico B2C (neto)
                // Multiplicar por IVA y mostrar
                if (!hasPVP) {
                    console.log('[PriceFix] Precio neto encontrado: $' + priceValue.toFixed(3) + 
                                ' → Con IVA: $' + priceWithIVA.toFixed(3));
                    
                    // Formatear con separadores chilenos
                    const formatted = formatPrice(priceWithIVA);
                    
                    // Reemplazar el contenido
                    el.textContent = '$ ' + formatted;
                    el.style.fontWeight = 'bold';
                    el.style.color = '#2c5aa0';
                    
                    processed++;
                }
                // Si tiene PVP cercano, es el precio con IVA, dejarlo como está
                else {
                    console.log('[PriceFix] Precio con IVA encontrado, sin cambios: $' + priceValue.toFixed(3));
                }
            }
        });

        console.log('[PriceFix] Precios procesados: ' + processed);
    }

    /**
     * Formatea un número como precio chileno
     * Ejemplo: 15900.1 → "15.900,10"
     */
    function formatPrice(value) {
        // Redondear a 2 decimales
        const rounded = Math.round(value * 100) / 100;
        
        // Separar enteros y decimales
        const parts = rounded.toFixed(2).split('.');
        const integer = parts[0];
        const decimals = parts[1];
        
        // Agregar puntos cada 3 dígitos
        const formatted = integer.replace(/\B(?=(\d{3})+(?!\d))/g, '.');
        
        return formatted + ',' + decimals;
    }

    /**
     * Ejecutar cuando esté listo
     */
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            console.log('[PriceFix] DOM listo');
            setTimeout(addIVAToPublicoB2C, 300);
        });
    } else {
        console.log('[PriceFix] DOM ya estaba listo');
        setTimeout(addIVAToPublicoB2C, 300);
    }

    /**
     * Observer para cambios posteriores (filtros, búsqueda, variantes)
     */
    const observer = new MutationObserver(function(mutations) {
        let hasChanges = false;
        
        for (let i = 0; i < mutations.length; i++) {
            const mutation = mutations[i];
            if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                hasChanges = true;
                break;
            }
        }

        if (hasChanges) {
            console.log('[PriceFix] Detectado cambio, re-procesando...');
            setTimeout(addIVAToPublicoB2C, 100);
        }
    });

    observer.observe(document.body, {
        childList: true,
        subtree: true
    });

    console.log('[PriceFix] Listo - esperando cambios');

})();
