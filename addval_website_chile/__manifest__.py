# -*- coding: utf-8 -*-
{
    'name': 'Addval Website Chile - RUT y Teléfono',
    'version': '16.0.1.0.0',
    'author': 'NLH Consultores SpA',
    'license': 'OPL-1',
    'category': 'Website/eCommerce',
    'summary': 'Validación de RUT chileno y formato de teléfono en el checkout del e-commerce',
    'description': """
        - Campo VAT renombrado a RUT con validación de dígito verificador (módulo 11)
        - RUT obligatorio en el formulario de checkout
        - Teléfono: auto-prefijo +56 si el usuario no lo ingresa
        - Validación server-side de ambos campos
    """,
    'depends': ['addval_website_address', 'website_sale', 'eq_website_default_code'],
    'data': [
        'views/website_sale_address.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'addval_website_chile/static/src/js/checkout_chile.js',
        ],
    },
    'installable': True,
    'auto_install': False,
}
