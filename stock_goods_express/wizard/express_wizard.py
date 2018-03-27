# coding: utf-8
import logging, json
from odoo.exceptions import UserError
from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class SendWizard(models.TransientModel):
    _inherit = "send.express.order"

    def confirm(self):
        super(SendWizard, self).confirm()
        if not self.picking_id or self.api != '1':
            return
        print('good_express')
        # 依次发送各订单信息
        for order in self.picking_id:
            if order.state == 'done' or order.picking_type_code != 'outgoing' or order.is_send:
                raise UserError('该订单：%s.已出库或该订单不是出库单' % order.name)
                # 手写快递单号进行发货
            if order.carrier_tracking_ref:
                # 订阅消息实时推送
                self.env['stock.goods.express'].Subscription_push(order.id)
            else:
                # 电子面单API获取物流运单号
                res = self.env['stock.goods.express'].get_number(order.id)
                search_message = json.loads(res)
                if search_message['Reason'] == '成功':
                    LogisticCode = search_message['Order']['LogisticCode']
                    # rintptemplate = search_message['PrintTemplate'] #电子面单
                    order.carrier_tracking_ref = LogisticCode
                    order.is_send = True
                    # 订阅消息实时推送
                    self.env['stock.goods.express'].Subscription_push(order.id)
                else:
                    raise UserError(u'警告:' + search_message['Reason'])
