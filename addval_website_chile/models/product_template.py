# -*- coding: utf-8 -*-
import logging
from odoo import models

_logger = logging.getLogger(__name__)

PRICELIST_IDS_B2C = [13, 16]
IVA_RATE = 1.19


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def _get_combination_info(self, combination=False, product_id=False,
                               add_qty=1, pricelist=False, **kwargs):
        res = super()._get_combination_info(
            combination=combination,
            product_id=product_id,
            add_qty=add_qty,
            pricelist=pricelist,
            **kwargs
        )
        pl = pricelist
        if not pl:
            try:
                pl = self.env['website'].get_current_website().get_current_pricelist()
            except Exception:
                pl = False

        if pl and pl.id in PRICELIST_IDS_B2C:
            price = res.get('price', 0)
            if price:
                res['price'] = round(price * IVA_RATE)
            list_price = res.get('list_price', 0)
            if list_price:
                res['list_price'] = round(list_price * IVA_RATE)

        return res
