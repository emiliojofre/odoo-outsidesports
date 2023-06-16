# -*- coding: utf-8 -*-
{
    'name': "Ajuste template email cobranza",

    'summary': """
        """,

    'description': """
        
    """,

    "author": "Addval Connect",
    "website": "http://www.addval.cl",
    "category": "Product",
    "license": "Other proprietary",
    'version': '0.1',

    'depends': ['base','account_followup'],

    'data': [
        #'security/ir.model.access.csv',
        'data/account_followup_data.xml'
    ],
    
    'installable': True,
    'application': True,
    'auto_install': False,
}