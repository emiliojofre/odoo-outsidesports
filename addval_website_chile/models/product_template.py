# -*- coding: utf-8 -*-
import logging

from odoo import models

_logger = logging.getLogger(__name__)

# Nombre técnico del sitio B2C tal como está en Website > Sitios.
# Se busca por nombre (no por ID) para que el módulo funcione igual
# en dev/test/prod aunque los IDs de website difieran entre ambientes.
B2C_WEBSITE_NAME = 'OUTSIDE SPORTS B2C'


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def _get_combination_info(self, combination=False, product_id=False,
                               add_qty=1, pricelist=False, parent_combination=False, **kwargs):
        res = super()._get_combination_info(
            combination=combination,
            product_id=product_id,
            add_qty=add_qty,
            pricelist=pricelist,
            parent_combination=parent_combination,
            **kwargs
        )

        website = self.env['website'].get_current_website()
        if not website or website.name != B2C_WEBSITE_NAME:
            # Cualquier otro sitio (ej. B2B) sigue exactamente igual que hoy.
            return res

        product = self.env['product.product'].browse(product_id) if product_id else False
        if not product or not product.exists():
            return res

        currency = website.currency_id or self.env.company.currency_id
        taxes = product.taxes_id.filtered(
            lambda t: t.company_id == self.env.company
        )

        for key in ('price', 'list_price'):
            base_amount = res.get(key)
            if not base_amount or not taxes:
                continue
            try:
                computed = taxes.compute_all(
                    base_amount,
                    currency=currency,
                    quantity=1,
                    product=product,
                    partner=False,
                )
                res[key] = computed['total_included']
            except Exception:
                _logger.exception(
                    "Chile B2C: no se pudo calcular el precio con IVA "
                    "incluido para el producto %s, se deja el precio original.",
                    product.display_name,
                )

        return res
