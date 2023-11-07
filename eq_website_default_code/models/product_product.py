from odoo import api, fields, models, _


class ProductProduct(models.Model):
    _inherit = 'product.product'

    product_product_pvp = fields.Float(
        'PVP Variante', default=1.0,
    )