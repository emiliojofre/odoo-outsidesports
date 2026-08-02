# -*- coding: utf-8 -*-
{
    'name': 'Addval Website B2B Login - Logout Fix',
    'summary': 'Corrige el 500 al cerrar sesión con addval_website_b2b_login (Odoo 16)',
    'description': """
Fix logout 500 for addval_website_b2b_login (Outside / Odoo 16)
================================================================

Production error on ``/web/session/logout``::

    File ".../addval_website_b2b_login/models/ir_http.py", line 55
        if not request.env.user._is_public():
    ValueError: Expected singleton: res.users()

Cause: logout uses ``auth='none'``, so ``request.env.user`` is empty and
``_is_public()`` crashes.

This companion module (does **not** replace Addval's module):

1. Skips Addval's ``_frontend_pre_dispatch`` for logout / empty user.
2. Forces ``auth='public'`` on ``/web/session/logout``.
    """,
    'author': 'NLH Consultores',
    'website': 'https://www.nlhconsultores.com',
    'category': 'Website/Website',
    'license': 'LGPL-3',
    'version': '16.0.1.0.0',
    'depends': ['website', 'addval_website_b2b_login'],
    'data': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
