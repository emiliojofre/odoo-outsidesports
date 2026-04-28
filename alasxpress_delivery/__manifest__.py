# -*- coding: utf-8 -*-
{
    'name': 'Alasxpress Shipping Integration - Outside Sports',
    'version': '16.0.1.2.0',
    'category': 'Inventory/Delivery',
    'summary': 'Integracion completa con Alasxpress WMS: Orders, Labels (PDF/ZPL), Status y Webhooks',
    'author': 'NLH Consultores SpA',
    'depends': ['stock', 'delivery', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/delivery_alas_data.xml',
        'views/delivery_carrier_views.xml',
        'views/stock_picking_views.xml',
    ],
    'installable': True,
    'license': 'OEEL-1',
}