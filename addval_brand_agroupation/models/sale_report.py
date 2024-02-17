# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleReport(models.Model):
    _inherit = 'sale.report'

    product_brand_id = fields.Many2one('wk.product.brand', related='product_tmpl_id.product_brand_id')

    def _from_sale(self):
        from_sale = super(SaleReport, self)._from_sale()
        from_sale += """
            LEFT JOIN wk_product_brand br ON br.id = t.product_brand_id
            """
        return from_sale

    def _select_sale(self):
        select_ = super(SaleReport, self)._select_sale()
        select_ += """,
            br.id AS product_brand_id"""
        return select_

    def _group_by_sale(self):
        group_by = super(SaleReport, self)._group_by_sale()
        group_by += """,
            br.id"""
        return group_by