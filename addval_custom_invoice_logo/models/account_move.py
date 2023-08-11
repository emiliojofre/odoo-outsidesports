# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = 'account.move'

    def get_custom_logo(self):

        header_data = super().get_header_data()

        order = self.env['sale.order'].search([
            ('name', '=', self.invoice_origin)
        ], limit =1)

        n2growth = 'N2Growth'

        if order and n2growth.upper() in order.analytic_account_id.name.upper():
            header_data['company_logo'] = '/addval_custom_invoice_logo/static/logo/Logo_Dark.png'

        return header_data