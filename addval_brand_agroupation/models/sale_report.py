from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class SaleReport(models.Model):
    _inherit = 'sale.report'

    product_brand_id = fields.Many2one('wk.product.brand', readonly=True)
    
    def _select_sale(self):
        select_ = super(SaleReport, self)._select_sale()
        select_ = select_.replace("p.product_tmpl_id,", "p.product_tmpl_id, t.product_brand_id AS product_brand_id,")
        _logger.info("### SELECT ###")
        _logger.info(select_)
        return select_

    def _group_by_sale(self):
        group_by = super(SaleReport, self)._group_by_sale()
        group_by += """,
            t.product_brand_id"""
        _logger.info("### GROUP BY ###")
        _logger.info(group_by)
        return group_by
