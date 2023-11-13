from odoo import api, fields, models, _


class ProductProduct(models.Model):
    _inherit = 'product.product'

    product_product_pvp = fields.Monetary(
        'PVP', default=1,currency_field='currency_id', compute='_compute_product_pvp'
    )


    @api.depends('list_price')
    def _compute_product_pvp(self):
        pricelist = self.env['product.pricelist'].search([('name', '=', 'Sugerido Público')], limit=1)
        if pricelist:
            for record in self:
                pricelist_item = self.env['product.pricelist.item'].search([
                    ('pricelist_id', '=', pricelist.id),
                    ('product_id', '=', record.id)
                ], limit=1)
                if pricelist_item:
                    price = pricelist_item.price.replace('$', '').replace(',', '').replace('\xa0', '').replace('.', '')
                    price_plus_iva = float(price)*1.19
                    record.product_product_pvp = price_plus_iva
                else:
                    record.product_product_pvp =  record.lst_price
        else:
            record.product_product_pvp =  record.lst_price