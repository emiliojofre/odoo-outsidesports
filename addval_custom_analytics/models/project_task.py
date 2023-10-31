# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
import logging
_logger = logging.getLogger(__name__)

class ProjectTask(models.Model):
    _inherit = 'project.task'

    def _get_area_domain(self):
        company = self.env['res.company'].sudo.search(['id', '=', self.company_id.id])
        company_plan =  company.area_analytic_plan_id
        return [("plan_id", "=", company_plan.id)]
    
    area_analytic_account_id = fields.Many2one(
        comodel_name='account.analytic.account',
        string="Área",
        copy=False, check_company=True,  # Unrequired company
        domain=_get_area_domain)
    
    def _get_activity_domain(self):
        return [("plan_id", "=", self.company_id.activity_analytic_plan_id.id)]
    
    activity_analytic_account_id = fields.Many2one(
        comodel_name='account.analytic.account',
        string="Actividad",
        copy=False, check_company=True,  # Unrequired company
        domain=_get_activity_domain)
    
