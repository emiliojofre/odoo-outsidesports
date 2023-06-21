# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import timedelta


class FollowupLine(models.Model):
    _inherit = 'account_followup.followup.line'
    _order = 'delay desc'
    
    def _get_next_date(self):
        self.ensure_one()
        return fields.Date.today() + timedelta(days=1)

    def _get_next_followup(self):
        self.ensure_one()
        return self.env['account_followup.followup.line'].search([('delay', '>', self.delay), ('company_id', '=', self.env.company.id)], order="delay desc", limit=1)
