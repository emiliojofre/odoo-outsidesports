# -*- coding: utf-8 -*-
{
    'name': 'OutsideSports - Alas Express Integration',
    'version': '16.0.1.0.0',
    'summary': 'Integración con Alas Express courier para despachos',
    'description': """
        Módulo de integración con la API de Alas Express (ALAS-Ce0).
        Permite crear órdenes de entrega, obtener etiquetas y hacer tracking
        directamente desde las órdenes de entrega de Odoo.
    """,
    'author': 'NLH Consultores SpA',
    'category': 'Inventory/Delivery',
    'depends': [
        'stock',
        'delivery',
        'sale_stock',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/delivery_carrier_data.xml',
        'data/cron_data.xml',
        'views/delivery_carrier_views.xml',
        'views/stock_picking_views.xml',
        'views/res_config_settings_views.xml',
        'wizard/alas_express_label_wizard_views.xml',
    ],
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'OPL-1',
}
