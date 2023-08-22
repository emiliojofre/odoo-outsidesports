# -*- coding: utf-8 -*-

from odoo import fields, models, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    product_standard_price = fields.Float(related='product_id.standard_price', string='Costo')
    standard_price = fields.Float(compute='_compute_get_standard_price', string='Costo', store=True, readonly=False)

    @api.multi
    @api.depends('product_id')
    def _compute_get_standard_price(self):
        for rec in self:
            if rec.standard_price == 0:
                rec.standard_price = rec.product_standard_price
