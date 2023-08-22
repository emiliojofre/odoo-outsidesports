# -*- coding: utf-8 -*-
{
    'name': "product_description",

    'summary': """
        Modulo para colocar solo la descripción del producto en pedidos de venta""",

    'description': """
        Modulo para colocar solo la descripción del producto en pedidos de venta
    """,

    'author': "Yudimar Misel, NLH Consultores",
    'website': "http://www.nlhconsultores.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'product', 'sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
    ],
    'images': [
        'static/description/icon.png'
    ],
    # only loaded in demonstration mode

    'demo': [
        'demo/demo.xml',
    ],
}
