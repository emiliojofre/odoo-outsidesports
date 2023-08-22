# -*- coding: utf-8 -*-
{
    'name': 'DTE Consumo de Folios Extras',
    'description': 'Extras para Consumo de Folios',
    'category': 'account',
    'version': '1.0.1',
    'author': 'Daniel Santibáñez Polanco',
    'summary': 'Facturación Electrónica para Chile. Mayor información en https://odoocoop.cl',
    'website': 'https://globalresponse.cl',
    'data': [
        'data/cron.xml',
        'views/res_config_settings.xml',
        'views/account_move_consumo_folios.xml',
    ],
    'depends': [
                'l10n_cl_fe',
            ],
    'application': True,
    'license': 'AGPL-3',
    'currency': 'EUR',
    'price': 40,
}
