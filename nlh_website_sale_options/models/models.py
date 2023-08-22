# -*- coding: utf-8 -*-

from odoo import models, fields, api

# class nlh_website_sale_options(models.Model):
#     _name = 'nlh_website_sale_options.nlh_website_sale_options'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100