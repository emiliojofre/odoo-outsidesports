# -*- coding: utf-8 -*-
{
    'name': "NLH Print Report",

    'description': """
        Long description of module's purpose
    """,

    'author': "NLH Consultores",
    'website': "http://www.nlhconsultores.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '1.20210407',

    # any module necessary for this one to work correctly
    'depends': ['l10n_cl_fe', 'stock', 'l10n_cl_stock_picking'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/stock_report_layout.xml',
        'views/account_invoice_report_layout.xml',
        'views/stock_delivery_ship_report.xml',
        'views/stock_picking.xml',
        'views/account_invoice.xml',
        'views/sale_order.xml'
    ],

}