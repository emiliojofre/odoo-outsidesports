# -*- coding: utf-8 -*-
{
    'name': 'Website B2B Login Required',
    'summary': 'Obliga login en el sitio web B2B y corrige el error 500 al cerrar sesión',
    'description': """
Website B2B Login (addval_website_b2b_login)
============================================

Fuerza autenticación en el frontend de los sitios web marcados como B2B
(website.b2b_login_required).

Los visitantes públicos son redirigidos a /web/login?redirect=<ruta>.

Rutas permitidas sin login: login, signup, reset password, logout,
assets estáticos e imágenes.

Fix logout: /web/session/logout usa auth=none y request.env.user puede
ser un res.users() vacío. Este módulo evita llamar _is_public() en ese
caso, incluye logout en la whitelist y fuerza auth=public en logout.
    """,
    'author': 'NLH Consultores / Addval',
    'website': 'https://www.nlhconsultores.com',
    'category': 'Website/Website',
    'license': 'LGPL-3',
    'version': '19.0.1.0.1',
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
