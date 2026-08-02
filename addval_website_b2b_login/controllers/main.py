# -*- coding: utf-8 -*-
from odoo import http
from odoo.addons.web.controllers.session import Session


class B2BLoginSession(Session):
    """Force auth='public' on logout (needed on Odoo 16)."""

    @http.route(auth='public')
    def logout(self, *args, **kw):
        return super().logout(*args, **kw)
