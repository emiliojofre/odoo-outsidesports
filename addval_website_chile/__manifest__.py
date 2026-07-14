# -*- coding: utf-8 -*-
{
    'name': 'Addval Website Chile - RUT, Teléfono y Precio IVA Incluido',
    'version': '16.0.7.0.0',
    'author': 'NLH Consultores SpA',
    'license': 'OPL-1',
    'category': 'Website/eCommerce',
    'summary': (
        'Validación de RUT chileno y teléfono en el checkout, y precio '
        'B2C con IVA incluido (solo tarifa final) en el sitio '
        'OUTSIDE SPORTS B2C, sin afectar otros sitios (ej. B2B).'
    ),
    'depends': [
        'addval_website_address',
        'website_sale',
        'eq_website_default_code',
        # Necesario NO por funcionalidad, sino para el orden de carga:
        # internal_credit_payment.WebsiteCreditPayment reimplementa
        # checkout_form_validate/_validate_address_values desde cero SIN
        # llamar a super(), cortando la cadena de herencia. Declararlo
        # como dependencia obliga a Odoo a cargar nuestro controlador
        # DESPUES (y por lo tanto ejecutarlo PRIMERO en la cadena de
        # override), para que nuestras correcciones (telefono, RUT,
        # comuna->city) se apliquen antes de que el metodo de ese modulo
        # corte la cadena. Confirmado via logs: sin esto, nuestro
        # checkout_form_validate nunca se ejecutaba.
        'internal_credit_payment',
    ],
    'data': [
        'views/website_sale_address.xml',
        'views/website_layout_chile.xml',
        'views/website_sale_product.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'addval_website_chile/static/src/css/price_fix.css',
            'addval_website_chile/static/src/js/checkout_chile.js',
            'addval_website_chile/static/src/js/product_price_fix.js',
        ],
    },
    'installable': True,
    'auto_install': False,
}
