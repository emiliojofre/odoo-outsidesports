# -*- coding: utf-8 -*-
from odoo import http

# class PrestahopCelmedia(http.Controller):
#     @http.route('/prestahop_celmedia/prestahop_celmedia/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/prestahop_celmedia/prestahop_celmedia/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('prestahop_celmedia.listing', {
#             'root': '/prestahop_celmedia/prestahop_celmedia',
#             'objects': http.request.env['prestahop_celmedia.prestahop_celmedia'].search([]),
#         })

#     @http.route('/prestahop_celmedia/prestahop_celmedia/objects/<model("prestahop_celmedia.prestahop_celmedia"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('prestahop_celmedia.object', {
#             'object': obj
#         })