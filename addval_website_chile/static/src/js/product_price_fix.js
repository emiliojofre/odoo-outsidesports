/**
 * Script FINAL - Reemplaza precio neto por precio CON IVA
 * En fichas de producto con variantes
 */

(function() {
    'use strict';
    
    console.log('[PriceFix] Iniciado');

    function replaceNetoWithIVA() {
        console.log('[PriceFix] Buscando precios netos para reemplazar por IVA');
        
        const allElements = document.querySelectorAll('*');
        let replaced = 0;

        allElements.forEach(function(el) {
            const text = el.textContent;
            
            // Si contiene "+ IVA" (precio neto)
            if (text.includes('+ IVA') && text.length < 150 && el.children.length === 0) {
                console.log('[PriceFix] Encontrado neto: ' + text.trim().slice(0, 50));
                
                // Extraer el número de precio
                // Patrón: "$ XXX.XXX + IVA" o "$ XXX.XXX + IVA ($ XXX.XXX / Unidad(es))"
                const priceMatch = text.match(/\$\s*([\d.,]+)\s*\+\s*IVA/);
                
                if (priceMatch) {
                    // Convertir el precio encontrado
                    const priceString = priceMatch[1];
                    const neto = parseFloat(priceString.replace(/\./g, '').replace(/,/g, '.'));
                    
                    // Calcular con IVA (19%)
                    const conIVA = neto * 1.19;
                    
                    // Formatear con separadores chilenos
                    const formatted = formatPrice(conIVA);
                    
                    console.log('[PriceFix] Neto: $' + neto.toFixed(3) + ' → Con IVA: $' + formatted);
                    
                    // Buscar si hay PVP cercano (en ficha de producto)
                    let parent = el.parentElement;
                    let hasPVP = false;
                    let depth = 0;
                    
                    while (parent && depth < 5) {
                        if (parent.textContent.includes('PVP')) {
                            hasPVP = true;
                            break;
                        }
                        parent = parent.parentElement;
                        depth++;
                    }
                    
                    // Si está en ficha de producto con PVP, reemplazar el precio neto
                    if (hasPVP) {
                        console.log('[PriceFix] Reemplazando en ficha de producto');
                        el.textContent = '$ ' + formatted + ' (IVA Incl.)';
                        replaced++;
                    }
                    // Si no hay PVP cercano, es listado - eliminar la fila
                    else {
                        console.log('[PriceFix] Eliminando fila de listado');
                        if (el.parentElement && el.parentElement.parentElement) {
                            el.parentElement.parentElement.removeChild(el.parentElement);
                            replaced++;
                        }
                    }
                }
            }
        });

        console.log('[PriceFix] Procesados: ' + replaced);
    }

    /**
     * Formatea un número como precio chileno
     * Ejemplo: 25900.1 → "25.900"
     */
    function formatPrice(value) {
        const rounded = Math.round(value);
        return rounded.toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.');
    }

    // Ejecutar UNA SOLA VEZ cuando cargue
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', replaceNetoWithIVA);
    } else {
        replaceNetoWithIVA();
    }

})();
