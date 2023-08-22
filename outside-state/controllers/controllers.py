# -*- coding: utf-8 -*-
from odoo import http

# class Outside-state(http.Controller):
#     @http.route('/outside-state/outside-state/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/outside-state/outside-state/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('outside-state.listing', {
#             'root': '/outside-state/outside-state',
#             'objects': http.request.env['outside-state.outside-state'].search([]),
#         })

#     @http.route('/outside-state/outside-state/objects/<model("outside-state.outside-state"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('outside-state.object', {
#             'object': obj
#         })