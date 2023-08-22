# -*- coding: utf-8 -*-
from odoo import http

# class ProductDescription(http.Controller):
#     @http.route('/product_description/product_description/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/product_description/product_description/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('product_description.listing', {
#             'root': '/product_description/product_description',
#             'objects': http.request.env['product_description.product_description'].search([]),
#         })

#     @http.route('/product_description/product_description/objects/<model("product_description.product_description"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('product_description.object', {
#             'object': obj
#         })