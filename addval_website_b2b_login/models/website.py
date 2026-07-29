# -*- coding: utf-8 -*-
from odoo import models
from odoo.http import request

B2B_WEBSITE_NAME = 'OUTSIDE SPORTS B2B'


class Website(models.Model):
    _inherit = 'website'

    def sale_get_order(self, force_create=False, update_pricelist=False):
        """
        Red de apoyo (además del bloqueo en ir_http): nunca crear ni
        recuperar un carrito para el usuario público en el sitio B2B,
        por si algún punto de entrada quedara sin cubrir. Scopeado
        SOLO a "OUTSIDE SPORTS B2B" - en cualquier otro sitio (B2C)
        se comporta exactamente igual que el Odoo original.
        """
        self.ensure_one()
        if self.name == B2B_WEBSITE_NAME and self.env.user._is_public():
            if request.session.get('sale_order_id'):
                request.session.pop('sale_order_id', None)
                request.session.pop('website_sale_cart_quantity', None)
            return self.env['sale.order']
        return super().sale_get_order(
            force_create=force_create,
            update_pricelist=update_pricelist,
        )
