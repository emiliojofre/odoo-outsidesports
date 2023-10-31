# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
import logging
_logger = logging.getLogger(__name__)

class ProjectTask(models.Model):
    _inherit = 'project.task'

    def _get_area_domain(self):

        task_company = self.company_id
        _logger.warning('****TASK COMPANY: %s', task_company)

        allowed_company = self.env.context['allowed_company_ids'][0]
        _logger.warning('****ALLOWED COMPANY: %s', allowed_company)

        user_company = self.env.user.company_id
        _logger.warning('****USER COMPANY: %s', user_company)
        
        company_plan =  user_company.area_analytic_plan_id
        _logger.warning('****PLAN_COMPANY: %s', company_plan)
        return [("plan_id", "=", company_plan.id)]
    
    area_analytic_account_id = fields.Many2one(
        comodel_name='account.analytic.account',
        string="Área",
        copy=False, 
        domain=_get_area_domain)
    
    def _get_activity_domain(self):

        task_company = self.company_id
        _logger.warning('****TASK COMPANY: %s', task_company)

        allowed_company = self.env.context['allowed_company_ids'][0]
        _logger.warning('****ALLOWED COMPANY: %s', allowed_company)

        user_company = self.env.user.company_id
        _logger.warning('****USER COMPANY: %s', user_company)
        
        company_plan =  user_company.area_analytic_plan_id
        _logger.warning('****PLAN_COMPANY: %s', company_plan)
        return [("plan_id", "=", company_plan.id)]
        return [("plan_id", "=", self.company_id.activity_analytic_plan_id.id)]
    
    activity_analytic_account_id = fields.Many2one(
        comodel_name='account.analytic.account',
        string="Actividad",
        copy=False,
        domain=_get_activity_domain)
    
