# -*- coding: utf-8 -*-
{
    'name': 'Website B2B Login Required',
    'summary': 'Obliga login en sitio B2B y corrige el 500 al cerrar sesión (Odoo 16)',
    'description': """
Website B2B Login (addval_website_b2b_login) — Odoo 16
======================================================

Fuerza autenticación en websites con ``b2b_login_required``.

Fix logout: en ``/web/session/logout`` (auth=none) ``request.env.user``
puede ser vacío; no se llama ``_is_public()`` en ese caso y logout queda
en whitelist.
    """,
    'author': 'NLH Consultores / Addval',
    'website': 'https://www.nlhconsultores.com',
    'category': 'Website/Website',
    'license': 'LGPL-3',
    'version': '16.0.1.0.1',
    'depends': ['website'],
    'data': [
        'views/website_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'auto_install': False,
    'application': False,
}
