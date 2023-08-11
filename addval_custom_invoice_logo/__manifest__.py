# -*- coding: utf-8 -*-
{
   'name': "Customización cartas cobranza",

    'summary': """
        Customización de módulo cobranza (account_followup)""",

    'description': """
        Customización de módulo cobranza (account_followup)
    """,

    "author": "Addval Connect",
    "website": "http://www.addval.cl",
    "category": "Product",
    "license": "Other proprietary",
    'version': '0.1',

    'depends': [
        'base',
        'account_followup'
    ],

    'data': [
        #'security/ir.model.access.csv',
        #'views/res_partner.xml',
    ],

    'installable': True,
    'application': True,
    'auto_install': False,
}