# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PurchaseApprovalManagement(models.Model):
    _name = "purchase.approval.management"
    _description = "Gerencia para las aprobaciones de ordenes de compra"

    name = fields.Char('Nombre gerente')

    approve_filter  = fields.Char(string='Filtro a usar en el flujo', 
        compute="_compute_filter",
        help="Se recomienda usar el siguiente formato: NOMBRE_APELLIDO, de esta manera se evitan los problemas en los filtros por espacios de más")

    company_id = fields.Many2one('res.company', string='Company', required=True,
        default=lambda self: self.env.company)

    @api.depends('name')
    def _compute_filter(self):
        self.ensure_one()
        upper_name = self.name.upper()

        replace_space = upper_name.replace(" ","_")

        self.approve_filter = replace_space