# -*- coding: utf-8 -*-
{
    'name': 'Addval Website Chile - RUT y Teléfono',
    'version': '16.0.1.1.0',
    'author': 'NLH Consultores SpA',
    'license': 'OPL-1',
    'category': 'Website/eCommerce',
    'summary': 'Validación de RUT chileno y formato de teléfono en el checkout del e-commerce B2C',
    'depends': ['addval_website_address', 'website_sale', 'eq_website_default_code'],
    'data': [
        'views/website_sale_address.xml',
        'views/product_price_display.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'addval_website_chile/static/src/js/checkout_chile.js',
            'addval_website_chile/static/src/js/product_price_fix.js',
        ],
    },
    'installable': True,
    'auto_install': False,
}
