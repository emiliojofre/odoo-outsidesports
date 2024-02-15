# -*- coding: utf-8 -*-
{
   'name': "Extension Módulo Firma",

    'summary': """
        Extension Módulo Firma (addval_sign_extension)""",

    'description': """
        Extension Módulo Firma (addval_sign_extension)
    """,

    "author": "Addval Connect",
    "website": "http://www.addval.cl",
    "category": "Product",
    "license": "Other proprietary",
    'version': '0.1',

    'depends': [
        'base',
        'sign'
    ],

    'data': [
        'data/mail_template.xml',
        # 'views/account_move.xml',
    ],

    'installable': True,
    'application': True,
    'auto_install': False,
}