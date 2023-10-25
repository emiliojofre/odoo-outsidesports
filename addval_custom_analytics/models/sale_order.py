# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
import logging
_logger = logging.getLogger(__name__)

READONLY_FIELD_STATES = {
    state: [('readonly', True)]
    for state in {'sale', 'done', 'cancel'}
}


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    area_analytic_account_id = fields.Many2one(
        comodel_name='account.analytic.account',
        string="Área",
        copy=False, check_company=True,  # Unrequired company
        states=READONLY_FIELD_STATES,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    
    activity_analytic_account_id = fields.Many2one(
        comodel_name='account.analytic.account',
        string="Actividad",
        copy=False, check_company=True,  # Unrequired company
        states=READONLY_FIELD_STATES,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
