# -*- coding: utf-8 -*-
{
    'name': "NLH Website Sale Options",
    'description': """
        Long description of module's purpose
    """,
    
    'author': "NLH Consultores",
    'website': "http://www.nlhconsultores.com",
    
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Website',
    'version': '1.0.20210707',
    
    # any module necessary for this one to work correctly
    'depends': ['website_sale_options'],
    
    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/assets.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
