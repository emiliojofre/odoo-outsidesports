import random
from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.http import request
from odoo.osv import expression
from odoo.tools import float_is_zero


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