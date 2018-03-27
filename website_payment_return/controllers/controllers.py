# -*- coding: utf-8 -*-
from odoo import http

# class WebsitePaymentReturn(http.Controller):
#     @http.route('/website_payment_return/website_payment_return/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/website_payment_return/website_payment_return/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('website_payment_return.listing', {
#             'root': '/website_payment_return/website_payment_return',
#             'objects': http.request.env['website_payment_return.website_payment_return'].search([]),
#         })

#     @http.route('/website_payment_return/website_payment_return/objects/<model("website_payment_return.website_payment_return"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('website_payment_return.object', {
#             'object': obj
#         })