# -*- coding: utf-8 -*-
from odoo import models
from odoo.http import request


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    @classmethod
    def _frontend_pre_dispatch(cls):
        """Avoid Addval B2B login crash on /web/session/logout (Odoo 16).

        Addval's hook calls ``request.env.user._is_public()`` at line 55.
        On logout (``auth='none'``) the user recordset is empty → singleton
        error. For those requests we only apply the standard lang cookie
        logic and **do not** call Addval's method.
        """
        path = request.httprequest.path or ''
        user = request.env.user

        if path.startswith('/web/session/logout') or not user:
            # Mirror http_routing._frontend_pre_dispatch (Odoo 16.0)
            lang_code = request.lang._get_cached('code')
            request.update_context(lang=lang_code)
            if request.httprequest.cookies.get('frontend_lang') != lang_code:
                request.future_response.set_cookie(
                    'frontend_lang',
                    lang_code,
                    max_age=365 * 24 * 3600,
                )
            return

        return super()._frontend_pre_dispatch()
