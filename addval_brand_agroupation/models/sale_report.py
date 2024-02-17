# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleReport(models.Model):
    _inherit = 'sale.report'

    product_brand_id = fields.Many2one('wk.product.brand', readonly=True)

    def _select_sale(self):
        select_ = super(SaleReport, self)._select_sale()
        select_ += """,
            t.product_brand_id AS product_brand_id"""
        return select_

    def _group_by_sale(self):
        group_by = super(SaleReport, self)._group_by_sale()
        group_by += """,
            t.product_brand_id"""
        return group_by