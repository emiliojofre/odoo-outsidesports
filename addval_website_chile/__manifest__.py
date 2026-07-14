# -*- coding: utf-8 -*-
{
    'name': 'Addval Website Chile - RUT, Teléfono y Precio IVA Incluido',
    'version': '16.0.6.3.0',
    'author': 'NLH Consultores SpA',
    'license': 'OPL-1',
    'category': 'Website/eCommerce',
    'summary': (
        'Validación de RUT chileno y teléfono en el checkout, y precio '
        'B2C con IVA incluido (solo tarifa final) en el sitio '
        'OUTSIDE SPORTS B2C, sin afectar otros sitios (ej. B2B).'
    ),
    'depends': ['addval_website_address', 'website_sale', 'eq_website_default_code'],
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
