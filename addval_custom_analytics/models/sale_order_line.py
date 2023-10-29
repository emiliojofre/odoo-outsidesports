# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
import logging
import json
_logger = logging.getLogger(__name__)

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    analytic_distribution = fields.Json()

    analytic_distribution_area = fields.Json(
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id), ('plan_id', '=', company_id.area_analytic__plan_id)]"
    ) 

    analytic_distribution_activity = fields.Json()

    analytic_distribution_domain = fields.Char(
        compute="_compute_analytic_distribution_domain",
        readonly=True,
        store=False,
    )

    @api.depends('plan_id')
    def _compute_analytic_distribution_domain(self):
        for rec in self:
            rec.analytic_distribution_domain = json.dumps(
                [('plan_id', '=', rec.company_id.project_analytic_plan_id)]
            )