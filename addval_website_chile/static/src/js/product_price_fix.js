/**
 * Agrega "(IVA Incl.)" al precio en ficha de producto
 */
document.addEventListener('DOMContentLoaded', function () {
    function addIvaLabel() {
        document.querySelectorAll('.product_price .oe_price').forEach(function (el) {
            if (!el.querySelector('.iva-incl')) {
                var label = document.createElement('small');
                label.className = 'text-muted ms-2 iva-incl';
                label.textContent = '(IVA Incl.)';
                el.appendChild(label);
            }
        });
    }
    addIvaLabel();
    var container = document.querySelector('.product_price') || document.body;
    new MutationObserver(addIvaLabel).observe(container, { childList: true, subtree: true });
});
