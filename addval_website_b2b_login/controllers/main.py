# -*- coding: utf-8 -*-
from odoo import http
from odoo.addons.web.controllers.session import Session


class B2BLoginSession(Session):
    """Force auth='public' on logout (needed on Odoo ≤16; website does this upstream later).

    Whitelisting logout in ``ir.http`` is still required: otherwise a public
    user would be redirected to /web/login in ``_frontend_pre_dispatch``
    *before* ``Session.logout`` runs and the session would never clear.
    """

    @http.route(auth='public')
    def logout(self, *args, **kw):
        return super().logout(*args, **kw)
