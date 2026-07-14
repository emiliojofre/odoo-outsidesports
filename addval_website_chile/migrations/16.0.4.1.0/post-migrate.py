# -*- coding: utf-8 -*-


def migrate(cr, version):
    """Corre al ACTUALIZAR el modulo cuando ya estaba instalado
    (ej. el ambiente de testing, donde el problema fue detectado)."""
    from odoo import api, SUPERUSER_ID
    from odoo.addons.addval_website_chile.hooks import _run_all_fixes

    env = api.Environment(cr, SUPERUSER_ID, {})
    _run_all_fixes(env)
