# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
import logging
_logger = logging.getLogger(__name__)

class PruchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    analytic_distribution_area = fields.Json(
        inverse="_inverse_analytic_distribution",
    ) 

    analytic_distribution_activity = fields.Json(
        inverse="_inverse_analytic_distribution",
    )