# -*- coding: utf-8 -*-
from odoo import models, fields, _
from odoo.exceptions import ValidationError


class AlasExpressRegionRate(models.Model):
    """Tarifa de envío Alas Express por región (estado) del país."""

    _name = 'alas.express.region.rate'
    _description = 'Tarifa Alas Express por Región'
    _order = 'state_id'

    carrier_id = fields.Many2one(
        'delivery.carrier',
        string='Método de Envío',
        required=True,
        ondelete='cascade',
        index=True,
    )
    country_id = fields.Many2one(
        'res.country',
        string='País',
        related='state_id.country_id',
        store=True,
        readonly=True,
    )
    state_id = fields.Many2one(
        'res.country.state',
        string='Región',
        required=True,
        ondelete='restrict',
        domain="[('country_id.code', '=', 'CL')]",
        help='Región de Chile a la que aplica esta tarifa de envío.',
    )
    price = fields.Float(
        string='Precio de Envío',
        required=True,
        default=0.0,
        digits='Product Price',
        help='Monto a cobrar por envíos con destino en esta región.',
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Moneda',
        related='carrier_id.company_id.currency_id',
        readonly=True,
    )
    company_id = fields.Many2one(
        'res.company',
        related='carrier_id.company_id',
        store=True,
        readonly=True,
    )

    _sql_constraints = [
        (
            'carrier_state_uniq',
            'unique(carrier_id, state_id)',
            'Ya existe una tarifa para esta región en el método de envío.',
        ),
    ]

    @api.constrains('price')
    def _check_price(self):
        for rec in self:
            if rec.price < 0:
                raise ValidationError(_(
                    'El precio de envío para la región "%s" no puede ser negativo.'
                ) % (rec.state_id.display_name or ''))

    def name_get(self):
        result = []
        for rec in self:
            name = '%s: %s' % (
                rec.state_id.name or _('Sin región'),
                rec.price,
            )
            result.append((rec.id, name))
        return result
