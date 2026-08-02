# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    b2b_login_required = fields.Boolean(
        related='website_id.b2b_login_required',
        readonly=False,
    )
