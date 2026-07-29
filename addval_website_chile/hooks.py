# -*- coding: utf-8 -*-
import logging

_logger = logging.getLogger(__name__)


def _fix_generic_view_xmlid(env, module, name):
    """
    Repara un problema de DATOS (no de arch/codigo): un xmlid como
    '<module>.<name>' puede haber quedado apuntando a una copia
    especifica de un sitio web (creada por el mecanismo Copy-On-Write
    de Odoo al editar esa vista desde el editor visual estando parado
    en ese sitio) en vez de apuntar a la vista GENERICA (sin
    website_id), que es la que cualquier otro modulo deberia heredar
    con inherit_id="<module>.<name>".

    Si eso pasa, cualquier vista que herede de ese xmlid (por ejemplo
    las nuestras) termina heredando del padre equivocado y nunca se
    aplica en los sitios que no sean ese uno especifico.

    Esta funcion:
      1. Busca la vista actualmente mapeada por el xmlid.
      2. Si ya apunta a la generica, no hace nada (idempotente).
      3. Busca sus "hermanas" (mismo campo `key`, que es lo que Odoo
         usa para agrupar las copias COW de una misma vista).
      4. Si encuentra una hermana generica (sin website_id), reapunta
         el xmlid hacia ella.
      5. Preserva la vista especifica de sitio que quedaba, creandole
         un xmlid propio si no tenia uno, para no perderla.

    Se puede llamar para cualquier par (module, name) donde se
    sospeche el mismo problema, no solo para address_custom.
    """
    View = env['ir.ui.view'].sudo()
    IMD = env['ir.model.data'].sudo()

    imd = IMD.search([('module', '=', module), ('name', '=', name)], limit=1)
    if not imd:
        _logger.info(
            "addval_website_chile: no existe el xmlid %s.%s, nada que reparar.",
            module, name,
        )
        return

    current_view = View.browse(imd.res_id)
    if not current_view.exists():
        return

    if not current_view.website_id:
        _logger.info(
            "addval_website_chile: el xmlid %s.%s ya apunta a la vista "
            "generica (view_id=%s). Nada que reparar.",
            module, name, current_view.id,
        )
        return

    siblings = View.with_context(active_test=False).search([
        ('key', '=', current_view.key),
    ])
    generic_view = siblings.filtered(lambda v: not v.website_id)[:1]

    if not generic_view:
        _logger.warning(
            "addval_website_chile: el xmlid %s.%s apunta a una vista "
            "especifica de sitio (view_id=%s, website=%s) y no se "
            "encontro ninguna vista generica hermana. No se modifica "
            "nada automaticamente - revisar manualmente.",
            module, name, current_view.id, current_view.website_id.name,
        )
        return

    old_view = current_view
    existing_xmlid_for_old = IMD.search([
        ('model', '=', 'ir.ui.view'), ('res_id', '=', old_view.id),
    ], limit=1)
    if not existing_xmlid_for_old:
        site_label = ''.join(
            ch if ch.isalnum() else '_'
            for ch in (old_view.website_id.name or 'site').lower()
        )
        IMD.create({
            'module': module,
            'name': '%s_%s_%s' % (name, site_label, old_view.id),
            'model': 'ir.ui.view',
            'res_id': old_view.id,
            'noupdate': True,
        })
        _logger.info(
            "addval_website_chile: se preservo la vista especifica de "
            "sitio (view_id=%s, website=%s) con un xmlid propio.",
            old_view.id, old_view.website_id.name,
        )

    imd.write({'res_id': generic_view.id})
    _logger.info(
        "addval_website_chile: xmlid %s.%s reapuntado de view_id=%s "
        "(sitio %s) a la vista generica view_id=%s.",
        module, name, old_view.id, old_view.website_id.name, generic_view.id,
    )


def _run_all_fixes(env):
    # address_custom: confirmado en testing (Emilio Jofre / Outside Sports).
    _fix_generic_view_xmlid(env, 'addval_website_address', 'address_custom')


def post_init_hook(cr, registry):
    """Corre al INSTALAR el modulo por primera vez (ej. produccion)."""
    from odoo import api, SUPERUSER_ID
    env = api.Environment(cr, SUPERUSER_ID, {})
    _run_all_fixes(env)
