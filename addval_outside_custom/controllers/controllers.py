# -*- coding: utf-8 -*-
from odoo import http
from odoo.exceptions import UserError
from odoo.http import request
from odoo.tools import ustr
from odoo.tools.pycompat import izip


class MyModule(http.Controller):

    def get_attribute_value_ids(self, product):
        """ list of selectable attributes of a product

        :return: list of product variant description
           (variant id, [visible attribute ids], variant price, variant sale price)
        """
        # product attributes with at least two choices
        quantity = product._context.get('quantity') or 1
        product = product.with_context(quantity=quantity)

        visible_attrs_ids = product.attribute_line_ids.filtered(lambda l: len(l.value_ids) > 1).mapped('attribute_id').ids
        to_currency = request.website.get_current_pricelist().currency_id
        attribute_value_ids = []
        for variant in product.product_variant_ids:
            if to_currency != product.currency_id:
                price = variant.currency_id.compute(variant.website_public_price, to_currency) / quantity
            else:
                price = variant.website_public_price / quantity
            visible_attribute_ids = [v.id for v in variant.attribute_value_ids if v.attribute_id.id in visible_attrs_ids]
            attribute_value_ids.append([variant.id, visible_attribute_ids, variant.website_price / quantity, price])

        variant_ids = [r[0] for r in attribute_value_ids]

        for r, variant in izip(attribute_value_ids, request.env['product.product'].sudo().browse(variant_ids)):
            r.extend([{
                'virtual_available': variant.virtual_available,
                'product_type': variant.type,
                'inventory_availability': variant.inventory_availability,
                'available_threshold': variant.available_threshold,
                'custom_message': variant.custom_message,
                'product_template': variant.product_tmpl_id.id,
                'cart_qty': variant.cart_qty,
                'uom_name': variant.uom_id.name,
            }])

        return attribute_value_ids
