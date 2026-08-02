# -*- coding: utf-8 -*-


def post_init_hook(env):
    """Enable B2B login on websites whose domain/name looks like a B2B site.

    Preserves Outside production behavior (b2b.outsidesports.cl) when the
    module is installed or replaced without manually re-checking the flag.
    """
    for website in env['website'].search([]):
        haystack = ' '.join(filter(None, [
            website.domain or '',
            website.name or '',
        ])).lower()
        if 'b2b' in haystack and not website.b2b_login_required:
            website.b2b_login_required = True
