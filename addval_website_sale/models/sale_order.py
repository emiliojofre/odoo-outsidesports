import random
from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.http import request
from odoo.osv import expression
from odoo.tools import float_is_zero

import logging
_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('website_id'):
                if 'company_id' in vals:
                    company = self.env['res.company'].browse(vals['company_id'])
                    analytic = company.api_analytic_id.id
                    vals['analytic_account_id'] = analytic
        return super().create(vals_list)
    
    def _prepare_order_line_update_values(self, order_line, quantity, linked_line_id=False, **kwargs):
        values = super(SaleOrder, self)._prepare_order_line_update_values(order_line, quantity, linked_line_id=linked_line_id, **kwargs)
        _logger.info("### _prepare_order_line_update_values ###")
        _logger.info(values)
        
        values['analytic_distribution'] = {self.analytic_account_id.id: 100}
        _logger.info(values)

        return values
    
    def _prepare_order_line_values(self, product_id, quantity, linked_line_id=False,
        no_variant_attribute_values=None, product_custom_attribute_values=None, **kwargs):
        values = super(SaleOrder, self)._prepare_order_line_update_values(product_id, quantity, linked_line_id=linked_line_id,
            no_variant_attribute_values=no_variant_attribute_values,
            product_custom_attribute_values=product_custom_attribute_values, **kwargs)
        _logger.info("### _prepare_order_line_values ###")
        _logger.info(values)
        return values