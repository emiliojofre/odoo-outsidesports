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
    
    def _get_country_related_render_values(self, kw, render_values):
        res = super()._get_country_related_render_values(kw, render_values)
        _logger.info("#################################")
        _logger.info(res)
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
    @route(['/my/account'], type='http', auth='user', website=True)
    def account(self, redirect=None, **post):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        values.update({
            'error': {},
            'error_message': [],
        })

        if post and request.httprequest.method == 'POST':
            error, error_message = self.details_form_validate(post)
            values.update({'error': error, 'error_message': error_message})
            values.update(post)
            if not error:
                values = {key: post[key] for key in self.MANDATORY_BILLING_FIELDS}
                values.update({key: post[key] for key in self.OPTIONAL_BILLING_FIELDS if key in post})
                for field in set(['country_id', 'state_id']) & set(values.keys()):
                    try:
                        values[field] = int(values[field])
                    except:
                        values[field] = False
                values.update({'zip': values.pop('zipcode', '')})
                self.on_account_update(values, partner)
                partner.sudo().write(values)
                if redirect:
                    return request.redirect(redirect)
                return request.redirect('/my/home')

        countries = request.env['res.country'].sudo().search([])
        states = request.env['res.country.state'].sudo().search([])
        cities = request.env["res.city"].sudo().search([("code", "!=", False)])

        values.update({
            'partner': partner,
            'countries': countries,
            'states': states,
            'has_check_vat': hasattr(request.env['res.partner'], 'check_vat'),
            'partner_can_edit_vat': partner.can_edit_vat(),
            'redirect': redirect,
            'page_name': 'my_details',
            'cities': cities
        })

        response = request.render("portal.portal_my_details", values)
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['Content-Security-Policy'] = "frame-ancestors 'self'"
        return response
