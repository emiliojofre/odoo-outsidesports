# -*- encoding: utf-8 -*-
from odoo import fields, models, api
from odoo.tools.translate import _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.onchange('city_id')
    def _onchange_city_id(self):
        if self.city_id:
            self.zip = self.city_id.zipcode
            self.state_id = self.city_id.state_id
            self.city = self.city_id.name
        else:
            self.zip = False
            self.state_id = False
            self.city = ""

