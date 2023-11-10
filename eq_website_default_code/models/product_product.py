from odoo import api, fields, models, _


class ProductProduct(models.Model):
    _inherit = 'product.product'

    product_product_pvp = fields.Monetary(
        'PVP', default=1,currency_field='currency_id', compute='_calcular_pvp'
    )

    def _calcular_pvp(self):

        product_base_pricelist = self.env['product.pricelist'].sudo().search([('name', '=', 'Sugerido Público')], limit=1)
        if product_base_pricelist:
            for item in product_base_pricelist.item_ids:
                for product in self:
                    if item.product_id.id == product.id:
                        pvp = item.price
                        break
                    else:
                        pvp = product.lst_price
        else:
            pvp = product.lst_price
        self.product_product_pvp = pvp

