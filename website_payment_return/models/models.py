# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    return_date = fields.Datetime(string=u'申请退款时间')
    com_return_date = fields.Datetime(string=u'确认时间')
    state = fields.Selection(selection_add=[
        ('not_refund', '拒绝退款'),
    ])

    def action_returns_commit(self):
        # ==================
        # 确认退款操作
        # ==================
        self.state = 'refunded'
        self.com_return_date = datetime.datetime.now()
        if self.sale_order_id.after_done_state in ['2', '3']:  # 当售后状态仅为退款、退货退款：已退款
            self.sale_order_id.after_done_state = '5'

        if self.sale_order_id.after_done_state == '4':  # 当售后状态为已退货：已退货退款
            self.sale_order_id.after_done_state = '6'

        if self.sale_order_id.after_done_state == '7':  # 当售后状态为拒绝退货：已退款拒绝退货
            self.sale_order_id.after_done_state = '11'

    def action_returns_refuse(self):
        # ==================
        # 拒绝退款操作
        # ==================
        self.state = 'not_refund'
        self.com_return_date = datetime.datetime.now()
        if self.sale_order_id.after_done_state in ['2', '3']:  # 当售后状态仅为退款、退货退款：拒绝退款
            self.sale_order_id.after_done_state = '8'

        if self.sale_order_id.after_done_state == '4':  # 当售后状态为已退货：已退货拒绝退款
            self.sale_order_id.after_done_state = '10'

        if self.sale_order_id.after_done_state == '7':  # 当售后状态为拒绝退货：拒绝退货退款
            self.sale_order_id.after_done_state = '9'
