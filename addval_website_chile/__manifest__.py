# -*- coding: utf-8 -*-
{
    'name': 'Addval Website Chile - RUT y Teléfono',
    'version': '16.0.2.0.3',
    'author': 'NLH Consultores SpA',
    'license': 'OPL-1',
    'category': 'Website/eCommerce',
    'summary': 'Precio B2C con IVA incluido, validación RUT y teléfono en checkout',
    'depends': ['addval_website_address', 'website_sale', 'eq_website_default_code'],
    'data': [
        'views/website_sale_address.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'addval_website_chile/static/src/js/checkout_chile.js',
            'addval_website_chile/static/src/js/product_price_fix.js',
            'addval_website_chile/static/src/css/price_fix.css',
        ],
    },
    'installable': True,
    'auto_install': False,
}
