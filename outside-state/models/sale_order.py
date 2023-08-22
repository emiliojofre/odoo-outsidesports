# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    def write(self, values):
        values.update({'name': self.product_id.name})
        res = super(SaleOrderLine, self).write(values)
        return res

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        result = super(SaleOrderLine, self).product_id_change()

        name = self.product_id.name
        # if self.product_id.description_sale:
        # 	name += '\n' + self.product_id.description_sale
        self.name = self.product_id.name
        self.update({'name': name})
        return result
