# -*- coding: utf-8 -*-
{
    'name': "NLH Prestahop",
    'version': '1.0',
    'summary': """Modulo para trabajar datos unicos en la integración con Prestashop""",
    'description': """
    Este modulo crea una llave unica por linea de producto en el presupuesto de venta que viene desde Prestashop, 
    para asi identificarle el estado en que se encuentra cada uno. Realiza la importacion mediante un archivo xls
    hacia el modulo de compras. Ejecuta un cambio de estado por linea de productos desde la aceptacion de la factura
    que viene desde SII. 

    """,
    'author': "NLH Consultores SpA",
    'website': "http://www.nlhconsultores.com",
    'support': 'ventas@nlhconsultores.com',
    'images': ['static/description/icon.png'],
    'category': 'tools',
    'depends': ['base', 'sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/inherit_sale_order_form.xml',
        'data/state.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'application': True,
}
