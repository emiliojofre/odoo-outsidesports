# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    See LICENSE file for full copyright and licensing details.
#################################################################################
from odoo import models, api, fields 

class CrmTeam(models.Model):
    _inherit = "sale.order"

    route_id = fields.Many2one('stock.location.route', string='Route', domain=[('sale_selectable', '=', True),('saleorder_selectable', '=', True)],
    default=False,
    )

class StockLocationRoute(models.Model):
    _inherit = "stock.location.route"

    saleorder_selectable = fields.Boolean('Sales Order', default=False)

class SaleOrderLine(models.Model):
    _inherit = ['sale.order.line']

    @api.model
    def create(self, vals):
        order_id = vals['order_id']
        order = self.env['sale.order'].browse(order_id)
        if order:
            if 	order.route_id:
                vals['route_id'] = order.route_id.id
        return super(SaleOrderLine, self).create(vals)
