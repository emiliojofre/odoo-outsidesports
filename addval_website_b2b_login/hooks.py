# -*- coding: utf-8 -*-
from odoo import SUPERUSER_ID, api


def post_init_hook(cr, registry):
    """Enable B2B login on websites whose domain/name contains 'b2b'."""
    env = api.Environment(cr, SUPERUSER_ID, {})
    for website in env['website'].search([]):
        haystack = ' '.join(filter(None, [
            website.domain or '',
            website.name or '',
        ])).lower()
        if 'b2b' in haystack and not website.b2b_login_required:
            website.b2b_login_required = True
