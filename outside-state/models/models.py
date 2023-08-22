# -*- coding: utf-8 -*-

from odoo import models, fields, api


class OutsideState(models.Model):
	_name = 'state.tp'
	
	name = fields.Char(string="Estado")
	shortcut = fields.Char(string="Abreviatura")


class InheritStockPicking(models.Model):
	_inherit = 'stock.picking'
	state_tp = fields.Many2one('state.tp', string='Estado de envio')
	carrier_name = fields.Char(string='Metodo de envio', compute='_get_carrier_id')
	
	@api.onchange('state_tp')
	def _get_carrier_id(self):
		for i in self:
			i.carrier_name = i.sale_id.carrier_id.name
