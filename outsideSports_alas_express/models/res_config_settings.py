# -*- coding: utf-8 -*-
from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # Placeholder por si se necesitan ajustes globales de Alas Express
    # a futuro (ej: modo sandbox/producción global)
    alas_express_env = fields.Selection(
        [('production', 'Producción')],
        string='Entorno Alas Express',
        default='production',
        config_parameter='alas_express.environment',
        readonly=True,
        help='Actualmente la API de Alas Express solo opera en producción.',
    )
