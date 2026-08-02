# -*- coding: utf-8 -*-
import werkzeug.exceptions

from odoo import models
from odoo.http import request

# El sitio que sirve realmente b2b.outsidesports.cl (confirmado en
# producción: website id=2) se llama literalmente "Outside Sports", NO
# "OUTSIDE SPORTS B2B" (ese otro registro, id=1, existe pero no tiene
# dominio asignado). Decisión del cliente: dejarlo así, sin mover el
# dominio - por eso el código reconoce este nombre en particular.
B2B_WEBSITE_NAME = 'Outside Sports'

# Rutas que SIEMPRE deben quedar accesibles sin sesion (para que el propio
# login, el registro y los assets estaticos puedan cargar); cualquier otra
# ruta del sitio B2B redirige a /web/login si el visitante es publico.
_EXCLUDED_PREFIXES = (
    '/web/login',
    '/web/signup',
    '/web/reset_password',
    '/web/session',
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
        resuelto (a diferencia de _pre_dispatch, que corre mas temprano
        y obliga a chequear manualmente si es frontend). Adaptado de un
        modulo similar hecho para Disandina
        (website_sale_force_login), agregando el scopeo por sitio (ahi
        no existia, y sin el se bloquearia tambien el B2C) y ampliando
        la proteccion a CUALQUIER pagina (no solo /shop*), ya que el
        requerimiento aqui es que no se vea nada del sitio sin iniciar
        sesion, incluida la portada.
        """
        super()._frontend_pre_dispatch()

        website = getattr(request, 'website', False)
        if not website or website.name != B2B_WEBSITE_NAME:
            return

        if not request.env.user._is_public():
            return

        path = request.httprequest.path or ''
        if any(path.startswith(p) for p in _EXCLUDED_PREFIXES):
            return

        werkzeug.exceptions.abort(
            request.redirect('/web/login?redirect=' + path, code=303)
        )
