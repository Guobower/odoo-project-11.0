# -*- coding: utf-8 -*-
from odoo import http

# class SfExpress(http.Controller):
#     @http.route('/sf_express/sf_express/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sf_express/sf_express/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('sf_express.listing', {
#             'root': '/sf_express/sf_express',
#             'objects': http.request.env['sf_express.sf_express'].search([]),
#         })

#     @http.route('/sf_express/sf_express/objects/<model("sf_express.sf_express"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sf_express.object', {
#             'object': obj
#         })