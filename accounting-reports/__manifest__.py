# -*- coding: utf-8 -*-
{
    'name': "accounting-reports",

    'summary': """
        Modulo para customizar los reportes de contabilidad""",

    'description': """
        Modulo para customizar los reportes de contabilidad
    """,

    'author': "TIDA",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base',
                'account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/analytic_report.xml',
        'views/checking_balance_report.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}