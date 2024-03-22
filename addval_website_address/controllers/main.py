# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import http
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request, route

_logger = logging.getLogger(__name__)


class WebsiteSaleAddressInfo(WebsiteSale):
    def _get_country_related_render_values(self, kw, render_values):
        res = super()._get_country_related_render_values(kw, render_values)
        country_state_cities = request.env["res.city"].search([("code", "!=", False)])
        res.update({"country_state_cities": country_state_cities})
        return res

    @http.route(
        [
            '/shop/state_infos/<model("res.country"):country>/<model("res.country.state"):state>'
        ],
        type="json",
        auth="public",
        methods=["POST"],
        website=True,
    )
    def state_infos(self, country, state, **kw):
        if country.id != state.country_id.id:
            return dict(in_country=False, use_selector=False, cities=[])
        cities = request.env["res.city"].search(
            [
                ("code", "!=", False),
                ("country_id", "=", country.id),
                ("state_id", "=", state.id),
            ]
        )
        use_selector = len(cities) > 0
        return dict(
            in_country=True,
            use_selector=use_selector,
            cities=cities.read(["id", "name"]),
        )


class PortalAddressInfo(CustomerPortal):
    @route(["/my/account"], type="http", auth="user", website=True)
    def account(self, redirect=None, **post):
        response = super().account(redirect, **post)
        cities = request.env["res.city"].sudo().search([("code", "!=", False)])
        response.update({"cities": cities})
        return response
