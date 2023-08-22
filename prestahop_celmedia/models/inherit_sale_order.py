from odoo import models, fields, api


class ProductState(models.Model):
    _name = 'state.product'

    name = fields.Char(string="Estado")
    shortcut = fields.Char(string="Abreviatura")


class InheritSaleOrder(models.Model):
    _inherit = 'sale.order.line'

    state_pres = fields.Many2one('state.product', string='Estado Prestashop')
