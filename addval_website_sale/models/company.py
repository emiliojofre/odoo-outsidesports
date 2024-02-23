from odoo import models, fields


class ResCompany(models.Model):
    _inherit = "res.company"

    api_analytic_id = fields.Many2one(
        'account.analytic.account',
        string = 'Cuenta analítica API',
        store = True,
        readonly=False,
    )