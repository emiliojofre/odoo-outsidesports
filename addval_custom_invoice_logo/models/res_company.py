# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
import logging
_logger = logging.getLogger(__name__)

class ResCompany(models.Model):
    _inherit = 'res.company'

    n2growth_logo = fields.Binary(string="N2Growth Logo")