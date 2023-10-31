from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    project_analytic_plan_id = fields.Many2one(
        'account.analytic.plan',
        string = 'Proyecto',
        store = True,
        readonly=False,
    )

    area_analytic__plan_id = fields.Many2one(
        'account.analytic.plan',
        related='',
        string = 'Área',
        store = True,
        readonly=False,
    )

    activity_analytic_plan_id = fields.Many2one(
        'account.analytic.plan',
        string = 'Actividad',
        store = True,
        readonly=False,
    )