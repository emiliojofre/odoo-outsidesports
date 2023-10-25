# -*- coding: utf-8 -*-
{
   'name': "Customización de plan analitico ",

    'summary': """
        Se añaden dos campos nuevos relacionasdos al plan analítco""",

    'description': """
        """,

    "author": "Addval Connect",
    "website": "http://www.addval.cl",
    "category": "Account",
    "license": "Other proprietary",
    'version': '0.1',

    'depends': [
        'base',
        'account',
        'sale',
        'account_accountant'
    ],

    'data': [
        #'security/ir.model.access.csv',
        'views/account_move.xml',
    ],

    'installable': True,
    'application': True,
    'auto_install': False,
}