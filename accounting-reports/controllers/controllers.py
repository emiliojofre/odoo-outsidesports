# -*- coding: utf-8 -*-
from odoo import http

# class Accounting-reports(http.Controller):
#     @http.route('/accounting-reports/accounting-reports/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/accounting-reports/accounting-reports/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('accounting-reports.listing', {
#             'root': '/accounting-reports/accounting-reports',
#             'objects': http.request.env['accounting-reports.accounting-reports'].search([]),
#         })

#     @http.route('/accounting-reports/accounting-reports/objects/<model("accounting-reports.accounting-reports"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('accounting-reports.object', {
#             'object': obj
#         })