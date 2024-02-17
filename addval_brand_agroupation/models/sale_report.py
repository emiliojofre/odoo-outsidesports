# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleReport(models.Model):
    _inherit = 'sale.report'

    product_brand_id = fields.Many2one('wk.product.brand', related='product_tmpl_id.product_brand_id')

    def _with_sale(self):
        return f"""{super()._with_sale()}
            LEFT JOIN product_template pt ON pt.id = t.product_tmpl_id
            LEFT JOIN wk_product_brand pb ON pb.id = pt.product_brand_id"""

    # Método para seleccionar el campo en la consulta SQL
    def _select_sale(self):
        select_ = f"""{super()._select_sale()},
            pt.product_brand_id AS product_brand_id"""
        return select_

    # Método para agrupar por el campo en la consulta SQL
    def _group_by_sale(self):
        group_by = f"""{super()._group_by_sale()},
            pt.product_brand_id"""
        return group_by