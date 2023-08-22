# -*- coding: utf-8 -*-
from odoo import http

# class Outside(http.Controller):
#     @http.route('/outside/outside/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/outside/outside/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('outside.listing', {
#             'root': '/outside/outside',
#             'objects': http.request.env['outside.outside'].search([]),
#         })

#     @http.route('/outside/outside/objects/<model("outside.outside"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('outside.object', {
#             'object': obj
#         })