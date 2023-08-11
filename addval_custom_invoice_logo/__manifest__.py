# -*- coding: utf-8 -*-
{
   'name': "Logo opcional para facturas ",

    'summary': """
        Se establece un logo distinto para productos de una marca específica""",

    'description': """
        Para las facturas que tengan una orden de venta con la cuenta analítica N2Growth cambiará el logo
    """,

    "author": "Addval Connect",
    "website": "http://www.addval.cl",
    "category": "Account",
    "license": "Other proprietary",
    'version': '0.1',

    'depends': [
        'base',
        'addval_accounting'
    ],

    'data': [
        #'security/ir.model.access.csv',
        #'views/res_partner.xml',
    ],

    'installable': True,
    'application': True,
    'auto_install': False,
}