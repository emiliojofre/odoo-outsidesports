# -*- coding: utf-8 -*-
from odoo import http

# class Outside2(http.Controller):
#     @http.route('/outside2/outside2/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/outside2/outside2/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('outside2.listing', {
#             'root': '/outside2/outside2',
#             'objects': http.request.env['outside2.outside2'].search([]),
#         })

#     @http.route('/outside2/outside2/objects/<model("outside2.outside2"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('outside2.object', {
#             'object': obj
#         })