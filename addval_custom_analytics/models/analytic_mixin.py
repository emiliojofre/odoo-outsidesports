from odoo import models, fields, api, _
from odoo.tools.float_utils import float_round, float_compare
from odoo.exceptions import UserError, ValidationError

class AnalyticMixin(models.AbstractModel):
    _inherit = 'analytic.mixin'

    analytic_distribution_area = fields.Json(
        'Área',
        compute='_compute_analytic_distribution_area', store=True, copy=True, readonly=False,
        precompute=True
    )

    analytic_distribution_activity = fields.Json(
        'Actividad',
        compute='_compute_analytic_distribution_activity', store=True, copy=True, readonly=False,
        precompute=True
    )

    analytic_distribution_area_search = fields.Json(
        store=False,
        search='_search_analytic_distribution_area'
    )

    analytic_distribution_activity_search = fields.Json(
        store=False,
        search='_search_analytic_distribution_activity'
    )

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        res = super().fields_get(allfields, attributes)
        if res.get('analytic_distribution_area_search'):
            res['analytic_distribution_area_search']['searchable'] = False
        if res.get('analytic_distribution_activity_search'):
            res['analytic_distribution_activity_search']['searchable'] = False
        return res
    
    def _compute_analytic_distribution_area(self):
        pass

    def _compute_analytic_distribution_activity(self):
        pass

    def _apply_analytic_distribution_domain(self, domain):
        return [
            ('analytic_distribution_search', leaf[1], leaf[2]) if len(leaf) == 3 and leaf[0] == 'analytic_distribution' and isinstance(leaf[2], str) else leaf
            for leaf in domain
        ]