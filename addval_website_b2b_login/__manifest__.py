# -*- coding: utf-8 -*-
{
    'name': 'Outside Sports B2B - Forzar Login',
    'version': '16.0.1.0.0',
    'author': 'NLH Consultores SpA',
    'license': 'OPL-1',
    'category': 'Website/Website',
    'summary': (
        'Exige iniciar sesión para ver cualquier página del sitio '
        'OUTSIDE SPORTS B2B (homepage, catálogo, todo) - sin afectar '
        'ningún otro sitio (ej. B2C).'
    ),
    'description': """
Adaptado de un módulo similar hecho para Disandina (website_sale_force_login),
con dos diferencias clave necesarias para este proyecto multi-sitio:

1. Scopeado SOLO al sitio "OUTSIDE SPORTS B2B" (por nombre) - el original
   no distinguia entre sitios, lo que habria bloqueado tambien al B2C.
2. Cubre CUALQUIER pagina del sitio (homepage incluida), no solo /shop* -
   el requerimiento es que no se vea nada en absoluto sin iniciar sesion,
   no solo la tienda.
""",
    'depends': ['website_sale'],
    'data': [],
    'installable': True,
    'auto_install': False,
}
