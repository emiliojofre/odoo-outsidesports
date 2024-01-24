from odoo import fields, models

class Project(models.Model):
    _inherit = "project.project"

    def _create_analytic_account(self):
        analytic_account = ''