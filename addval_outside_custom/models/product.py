from odoo import models, fields, http
from odoo.http import request

class ProductTemplate(models.Model):
    _inherit ='product.template'

    def _get_combination_info(self, combination=False, product_id=False, add_qty=1, pricelist=False, parent_combination=False, only_template=False):

        self.ensure_one()

        combination_info = super(ProductTemplate, self)._get_combination_info(
            combination=combination, product_id=product_id, add_qty=add_qty, pricelist=pricelist,
            parent_combination=parent_combination, only_template=only_template)

        combination_info['default_code'] = self.default_code