# -*- coding: utf-8 -*-
from odoo import models

B2C_WEBSITE_NAME = 'OUTSIDE SPORTS B2C'


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def _get_combination_info(self, combination=False, product_id=False,
                               add_qty=1, pricelist=False, **kwargs):
        """
        Sobrescribe combination_info para el sitio B2C:
        - Toma el precio neto de la tarifa Publico B2C
        - Aplica IVA 19%
        - Retorna ese precio como 'price' para que Odoo lo muestre
        """
        res = super()._get_combination_info(
            combination=combination,
            product_id=product_id,
            add_qty=add_qty,
            pricelist=pricelist,
            **kwargs
        )

        # Solo aplicar en el sitio B2C
        try:
            website = self.env['website'].get_current_website()
            if website.name != B2C_WEBSITE_NAME:
                return res
        except Exception:
            return res

        # Calcular precio con IVA (19%)
        price_neto = res.get('price', 0)
        if price_neto:
            price_con_iva = round(price_neto * 1.19)
            res['price'] = price_con_iva
            res['list_price'] = price_con_iva

        return res
