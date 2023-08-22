# -*- coding: utf-8 -*-

from odoo import fields, models, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    res_bank_account = fields.Char(compute='_res_bank_account', string='Banco', store=False)
    res_account_name = fields.Char(compute='_res_bank_account', string='Cuenta Bancaria', store=False)
    
    @api.multi
    def _res_bank_account(self):
        partner = self.env.user.company_id.partner_id
        bank_data = self.env['res.partner.bank'].search([('partner_id', '=', partner.id)], limit=1)

        for partner in self:
            partner.res_bank_account = bank_data.bank_id.name
            partner.res_account_name = bank_data.acc_number

