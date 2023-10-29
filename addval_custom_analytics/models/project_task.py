# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
import logging
_logger = logging.getLogger(__name__)

class ProjectTask(models.Model):
    _inherit = 'project.task'

    area_analytic_account_id = fields.Many2one(
        comodel_name='account.analytic.account',
        string="Área",
        copy=False, check_company=True,  # Unrequired company
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id), ('plan_id', '=', company_id.area_analytic__plan_id)]")
    
    activity_analytic_account_id = fields.Many2one(
        comodel_name='account.analytic.account',
        string="Actividad",
        copy=False, check_company=True,  # Unrequired company
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id), ('plan_id', '=', company_id.activity_analytic_plan_id)]")