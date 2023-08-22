# -*- coding: utf-8 -*-
from odoo import http

# class NlhPrintReport(http.Controller):
#     @http.route('/nlh_print_report/nlh_print_report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/nlh_print_report/nlh_print_report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('nlh_print_report.listing', {
#             'root': '/nlh_print_report/nlh_print_report',
#             'objects': http.request.env['nlh_print_report.nlh_print_report'].search([]),
#         })

#     @http.route('/nlh_print_report/nlh_print_report/objects/<model("nlh_print_report.nlh_print_report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('nlh_print_report.object', {
#             'object': obj
#         })