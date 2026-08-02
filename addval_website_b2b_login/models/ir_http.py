# -*- coding: utf-8 -*-

from odoo import models
from odoo.http import request

# El sitio que sirve realmente b2b.outsidesports.cl
B2B_WEBSITE_NAME = "Outside Sports"

# Rutas permitidas sin autenticación
_EXCLUDED_PREFIXES = (
    "/web/login",
    "/web/signup",
    "/web/reset_password",
    "/web/session",
    "/web/session/logout",
    "/web/logout",
    "/web/webclient",
    "/web/assets",
    "/web/static",
    "/website/static",
    "/website/translations",
    "/favicon.ico",
    "/robots.txt",
    "/sitemap.xml",
)


class IrHttp(models.AbstractModel):
    _inherit = "ir.http"

    @classmethod
    def _frontend_pre_dispatch(cls):
        super()._frontend_pre_dispatch()

        website = getattr(request, "website", False)
        if not website or website.name != B2B_WEBSITE_NAME:
            return

        path = request.httprequest.path or ""

        # Nunca interceptar estas rutas
        if any(path.startswith(prefix) for prefix in _EXCLUDED_PREFIXES):
            return

        user = request.env.user

        # Durante logout o antes de resolverse el usuario
        # puede no existir un singleton.
        if len(user) != 1:
            return

        if not user._is_public():
            return

        return request.redirect(
            "/web/login?redirect=" + path,
            code=303,
        )