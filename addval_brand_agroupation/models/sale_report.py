# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleReport(models.Model):
    _inherit = 'sale.report'

    product_brand_id = fields.Many2one('wk.product.brand', related='product_tmpl_id.product_brand_id')

    def _from_sale(self):
        from_ = """
            sale_order_line l
            LEFT JOIN sale_order s ON s.id=l.order_id
            JOIN res_partner partner ON s.partner_id = partner.id
            LEFT JOIN product_product p ON l.product_id=p.id
            LEFT JOIN product_template t ON p.product_tmpl_id=t.id
            LEFT JOIN uom_uom u ON u.id=l.product_uom
            LEFT JOIN uom_uom u2 ON u2.id=t.uom_id
            LEFT JOIN wk_product_brand br ON br.id = t.product_brand_id
            JOIN {currency_table} ON currency_table.company_id = s.company_id
            """.format(
            currency_table=self.env['res.currency']._get_query_currency_table(
                {
                    'multi_company': True,
                    'date': {'date_to': fields.Date.today()}
                }),
            )
        return from_

    def _select_sale(self):
        select_ = super(SaleReport, self)._select_sale()
        select_ += """,
            br.product_brand_id AS product_brand_id"""
        return select_

    def _group_by_sale(self):
        group_by = super(SaleReport, self)._group_by_sale()
        group_by += """,
            br.product_brand_id"""
        return group_by