# -*- coding: utf-8 -*-

from odoo import http, _
from odoo.exceptions import AccessError
from odoo.http import request
from odoo.tools import consteq
from werkzeug.utils import redirect
import datetime
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager


class WebsiteSaleExpress(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(WebsiteSaleExpress, self)._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        parent = request.env['res.partner'].sudo().search([('parent_id', '=', partner.id)]).id
        stock = request.env['stock.picking']

        order_count = stock.sudo().search_count([
            ('partner_id', 'in', [partner.id, parent]),
            # ('state', 'in', ['done']),
            ('picking_type_code', '=', 'outgoing')
        ])

        values.update({
            'express_count': order_count,
        })
        return values

    @http.route(['/my/express_orders', '/my/express_orders/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_express_orders(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        partner = request.env.user.partner_id
        parent = request.env['res.partner'].sudo().search([('parent_id', '=', partner.id)]).id
        domain = [
            ('partner_id', 'in', [partner.id, parent]),
            # ('state', 'in', ['done']),
            ('picking_type_code', '=', 'outgoing')
        ]

        searchbar_sortings = {
            'scheduled_date': {'label': _('交货日期'), 'express_order': 'scheduled_date desc'},
            'name': {'label': _('发货订单号'), 'express_order': 'name'},
            'carrier_tracking_ref': {'label': _('物流单号'), 'express_order': 'carrier_tracking_ref'},
        }

        Order = request.env['stock.picking']
        # default sortby order
        if not sortby:
            sortby = 'scheduled_date'

        # archive_groups = self.sudo()._get_archive_groups('stock.picking', domain)
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # count for pager
        order_count = Order.sudo().search_count(domain)

        # pager
        pager = portal_pager(
            url="/my/express_orders",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=order_count,
            page=page,
            step=self._items_per_page
        )

        # content according to pager and archive selecte
        res = Order.sudo().search(domain, order=sortby, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_orders_history'] = res.ids[:100]
        values = {
            'express_orders': res,
            'date': date_begin,
            'page_name': 'express_orders',
            'pager': pager,
            'default_url': '/my/express_orders',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        }
        return request.render("website_sale_express.portal_my_express_orders", values)

    def _order_get_page_data_values(self, order, access_token, **kwargs):
        sale_order = request.env['sale.order'].sudo().search([('name', '=', order.origin)])
        values = {
            'express_order': order,
            'sale_order': sale_order,
        }
        if access_token:
            values['no_breadcrumbs'] = True
            values['access_token'] = access_token

        if kwargs.get('error'):
            values['error'] = kwargs['error']
        if kwargs.get('warning'):
            values['warning'] = kwargs['warning']
        if kwargs.get('success'):
            values['success'] = kwargs['success']

        history = request.session.get('my_orders_history', [])
        values.update(get_records_pager(history, order))

        return values

    @http.route(['/my/express_orders/<int:order>'], type='http', auth="public", website=True)
    def portal_express_orders_page(self, order=None, access_token=None, **kw):
        order_sudo = request.env['stock.picking'].sudo().search([('id', '=', order)])
        if order_sudo:
            values = self._order_get_page_data_values(order_sudo, access_token, **kw)
        else:
            return request.redirect('/my')
        return request.render("website_sale_express.portal_express_order_page", values)

    #
    @http.route('/my/orders_cancel/<int:id>', type='http', auth="public", website=True)
    def website_cancel_order(self, id=None, **kw):
        if id:
            res = request.env['sale.order'].sudo().browse(id)
            if res.state == 'sent':
                res.state = 'draft'

        return redirect('/my/quotes')

    @http.route('/my/sale_orders_cancel/<int:id>', type='http', auth="public", website=True)
    def website_sale_cancel_order(self, id=None, **kw):
        if id:
            res = request.env['sale.order'].sudo().browse(id)
            if res.state == 'done':
                res_payment = request.env['payment.transaction'].sudo().search([('sale_order_id', '=', id)])
                if res_payment.state == 'refunding':
                    res_payment.state = 'done'

                stock = request.env['stock.picking'].sudo().search(
                    [('sale_id', '=', id), ('picking_type_code', '=', 'outgoing')])
                for stock in stock:
                    stock.after_done_state = False

                res.after_done_state = False

        return redirect('/my/orders')

    # 申请退款
    @http.route('/my/orders_cancel_1/<int:id>', type='http', auth="public", website=True)
    def website_cancel_order_1(self, id=None, **kw):
        if id:
            res = request.env['payment.transaction'].sudo().search([('sale_order_id', '=', id)])
            for res in res:
                if res.state == 'done':
                    res.state = 'refunding'
                    res.return_date = datetime.datetime.now()
            res_order = request.env['sale.order'].sudo().browse(id)
            if res_order.state == 'done':
                res_order.after_done_state = '2'
        return redirect('/my/orders')

    # 申请退货
    @http.route('/my/orders_cancel_2/<int:id>', type='http', auth="public", website=True)
    def website_cancel_order_2(self, id=None, **kw):
        if id:
            res = request.env['sale.order'].sudo().browse(id)
            if res.state == 'done':
                res.after_done_state = '1'

            stock = request.env['stock.picking'].sudo().search(
                [('sale_id', '=', id), ('picking_type_code', '=', 'outgoing')])
            for stock in stock:
                stock.after_done_state = 'refunding'
                stock.return_date = datetime.datetime.now()

        return redirect('/my/orders')

    # 退货退款
    @http.route('/my/orders_cancel_3/<int:id>', type='http', auth="public", website=True)
    def website_cancel_order_3(self, id=None, **kw):
        if id:
            stock = request.env['stock.picking'].sudo().search(
                [('sale_id', '=', id), ('picking_type_code', '=', 'outgoing')])
            for stock in stock:
                stock.after_done_state = 'refunding'
                stock.return_date = datetime.datetime.now()
            res = request.env['payment.transaction'].sudo().search([('sale_order_id', '=', id)])
            for res in res:
                if res.state == 'done':
                    res.state = 'refunding'
                    res.return_date = datetime.datetime.now()
            res_order = request.env['sale.order'].sudo().browse(id)
            if res_order.state == 'done':
                res_order.after_done_state = '3'
        return redirect('/my/orders')
