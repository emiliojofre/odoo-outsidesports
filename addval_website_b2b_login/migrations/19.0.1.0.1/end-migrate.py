# -*- coding: utf-8 -*-


def migrate(cr, version):
    """Re-enable B2B login on websites whose domain/name contains 'b2b'."""
    from odoo import SUPERUSER_ID, api

    env = api.Environment(cr, SUPERUSER_ID, {})
    if 'b2b_login_required' not in env['website']._fields:
        return
    for website in env['website'].search([('b2b_login_required', '=', False)]):
        haystack = ' '.join(filter(None, [
            website.domain or '',
            website.name or '',
        ])).lower()
        if 'b2b' in haystack:
            website.b2b_login_required = True
