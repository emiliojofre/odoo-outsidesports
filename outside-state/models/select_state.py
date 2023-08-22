# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from odoo.exceptions import UserError


class SelectState(models.Model):
    _name = 'select.state'
    _description = 'Cambiar estado de envio'
    state_id = fields.Many2one('state.tp', 'Estados de envio')

    def update_state(self):
        stock_picking_obj = self.env['stock.picking'].browse(self._context.get('active_ids', []))
        for state in stock_picking_obj:
            state.update({'state_tp': self.state_id})
