# -*- coding: utf-8 -*-
from odoo import http
from odoo.addons.web.controllers.session import Session


class B2BLoginLogoutFixSession(Session):
    """Force auth='public' on logout (website does this natively from 17.2+)."""

    @http.route(auth='public')
    def logout(self, *args, **kw):
        return super().logout(*args, **kw)
