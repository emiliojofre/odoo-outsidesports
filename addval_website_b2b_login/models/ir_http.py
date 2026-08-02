# -*- coding: utf-8 -*-
import logging

import werkzeug.exceptions

from odoo import models
from odoo.http import request

_logger = logging.getLogger(__name__)

_B2B_LOGIN_WHITELIST_PREFIXES = (
    '/web/login',
    '/web/signup',
    '/web/reset_password',
    '/web/session/logout',
    '/web/session/authenticate',
    '/web/assets/',
    '/web/content/',
    '/web/image/',
    '/web/binary/',
    '/web/static/',
    '/web/webclient/',
    '/website/translations',
    '/web/service-worker.js',
)


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    @classmethod
    def _addval_b2b_path_whitelisted(cls, path):
        if not path:
            return True
        for prefix in _B2B_LOGIN_WHITELIST_PREFIXES:
            if path == prefix.rstrip('/') or path.startswith(prefix):
                return True
        return False

    @classmethod
    def _frontend_pre_dispatch(cls):
        """Force login on B2B websites; never crash on auth='none' (logout).

        Production crash was::

            if not request.env.user._is_public():
            ValueError: Expected singleton: res.users()
        """
        super()._frontend_pre_dispatch()

        website = getattr(request, 'website', None)
        if not website or not website.b2b_login_required:
            return

        path = request.httprequest.path or ''
        if cls._addval_b2b_path_whitelisted(path):
            return

        user = request.env.user
        if not user:
            return

        if not user._is_public():
            return

        redirect_target = path
        query = request.httprequest.query_string
        if query:
            redirect_target = '%s?%s' % (
                path,
                query.decode() if isinstance(query, bytes) else query,
            )
        werkzeug.exceptions.abort(
            request.redirect(
                '/web/login?redirect=%s' % redirect_target,
                code=303,
            )
        )
