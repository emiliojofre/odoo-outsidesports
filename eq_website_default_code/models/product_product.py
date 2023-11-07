from odoo import api, fields, models, _


class ProductProduct(models.Model):
    _inherit = 'product.product'

    product_product_pvp = fields.Monetary(
        'PVP', default=1,currency_field='currency_id'
    )