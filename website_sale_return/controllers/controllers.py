# -*- coding: utf-8 -*-
from odoo import http

# class WebsiteSaleReturn(http.Controller):
#     @http.route('/website_sale_return/website_sale_return/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/website_sale_return/website_sale_return/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('website_sale_return.listing', {
#             'root': '/website_sale_return/website_sale_return',
#             'objects': http.request.env['website_sale_return.website_sale_return'].search([]),
#         })

#     @http.route('/website_sale_return/website_sale_return/objects/<model("website_sale_return.website_sale_return"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('website_sale_return.object', {
#             'object': obj
#         })