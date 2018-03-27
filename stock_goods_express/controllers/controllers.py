# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import logging
import json

_logger = logging.getLogger(__name__)


class CtSalesLogin(http.Controller):
    _notify_url = '/logistics/notify'

    @http.route('/logistics/notify', auth='public', type='http', methods=['POST'], csrf=False)
    def list(self, **kw):
        _logger.info('物流: 回调测试接口DataSign %s', kw)

        post = kw['RequestData']
        data_post = json.loads(post)
        data = data_post['Data']

        EBusinessID = data_post.get('EBusinessID')
        PushTime = data_post.get('PushTime')
        OrderCode = data[0]['OrderCode']  # 订单编号
        LogisticCode = data[0]['LogisticCode']  # 快递单号
        CallBack = data[0]['CallBack']  # 订单编号
        Traces = data[0]['Traces']  # 物流信息
        pick = request.env['stock.picking'].sudo().search(
            ['|', '|', ('name', '=', OrderCode), ('carrier_tracking_ref', '=', LogisticCode), ('name', '=', CallBack)])
        message_id = request.env['message.logistics'].sudo().search([('picking_id', '=', int(pick.id))])
        for unlink_id in message_id:
            unlink_id.unlink()
        if pick:
            for list in Traces:
                valus = {
                    'ftime': list['AcceptTime'],
                    'message': list['AcceptStation'],
                    'picking_id': int(pick.id),
                }
                request.env['message.logistics'].sudo().create(valus)
        data_post = {
            "EBusinessID": EBusinessID,
            "UpdateTime": PushTime,
            "Success": True,
            "Reason": ""
        }

        b = json.dumps(data_post)
        return b
