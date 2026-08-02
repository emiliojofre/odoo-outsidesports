# -*- coding: utf-8 -*-

from odoo import models
from odoo.http import request

# El sitio que sirve realmente b2b.outsidesports.cl (confirmado en
# producción: website id=2) se llama literalmente "Outside Sports", NO
# "OUTSIDE SPORTS B2B" (ese otro registro, id=1, existe pero no tiene
# dominio asignado). Decisión del cliente: dejarlo así, sin mover el
# dominio - por eso el código reconoce este nombre en particular.
B2B_WEBSITE_NAME = 'Outside Sports'

# Rutas que SIEMPRE deben quedar accesibles sin sesión (para que el propio
# login, el registro y los assets estáticos puedan cargar); cualquier otra
# ruta del sitio B2B redirige a /web/login si el visitante es público.
_EXCLUDED_PREFIXES = (
    '/web/login',
    '/web/signup',
    '/web/reset_password',
    '/web/session',
    '/web/session/logout',
    '/web/logout',
    '/web/webclient',
    '/web/assets',
    '/web/static',
    '/website/static',
    '/website/translations',
    '/favicon.ico',
    '/robots.txt',
    '/sitemap.xml',
)


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    @classmethod
    def _frontend_pre_dispatch(cls):
        """
        Se ejecuta en CADA request de frontend, ya con request.website
        resuelto (a diferencia de _pre_dispatch, que corre más temprano
        y obliga a chequear manualmente si es frontend).

        Si el sitio es el B2B:
        - Usuario autenticado -> acceso normal.
        - Usuario público -> redirigir al login.
        """

        super()._frontend_pre_dispatch()

        website = getattr(request, 'website', False)
        if not website or website.name != B2B_WEBSITE_NAME:
            return

        path = request.httprequest.path or ''

        # Nunca interceptar estas rutas
        if any(path.startswith(p) for p in _EXCLUDED_PREFIXES):
            return

        user = request.env.user

        # Durante /web/session/logout Odoo puede dejar request.env.user vacío.
        # Evita el:
        # ValueError: Expected singleton: res.users()
        if len(user) != 1:
            return

        # Usuario autenticado
        if not user._is_public():
            return

        # Usuario público -> obligar login
        return request.redirect(
            '/web/login?redirect=' + path,
            code=303,
        )