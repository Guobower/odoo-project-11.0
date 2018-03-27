# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    after_done_state = fields.Selection([('refunding', u'退货中'), ('not_refunded', u'拒绝退货'), ('refunded', u'退货完成')],
                                        string=u'售后状态')
    return_date = fields.Datetime(string=u'申请退货时间')
    com_return_date = fields.Datetime(string=u'确认退货时间')

    def action_return_refund(self):
        if self.state != 'done':
            raise UserError('订单未发货，请直接取消该订单即可。')
        else:
            self.after_done_state = 'not_refunded'
            order_id = self.sale_id
            if order_id.after_done_state in ['1', '3']:  # 当售后状态仅为退货、退货退款：拒绝退货
                order_id.after_done_state = '7'
            if order_id.after_done_state == '5':  # 当售后状态为已退款：已退款拒绝退货
                order_id.after_done_state = '11'
            if order_id.after_done_state == '8':  # 当售后状态为拒绝退款：拒绝退货退款
                order_id.after_done_state = '9'

    @api.multi
    def action_cancel(self):
        if self.after_done_state == 'refunding':
            self.after_done_state = 'refunded'
        return super(StockPicking, self).action_cancel()


class ReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'

    def create_returns(self):
        # ==================
        # 确认退货操作
        # ==================

        if self.state != 'done':
            raise UserError('订单未发货，请直接取消该订单即可。')
        else:

            for wizard in self:
                new_picking_id, pick_type_id = wizard._create_returns()

            order_id = self.picking_id.sale_id
            if order_id.after_done_state in ['1', '3']:  # 当售后状态仅为退货、退货退款：已退货
                order_id.after_done_state = '3'

            if order_id.after_done_state == '5':  # 当售后状态为已退款：已退货退款
                order_id.after_done_state = '6'

            if order_id.after_done_state == '8':  # 当售后状态为拒绝退款：已退货拒绝退款
                order_id.after_done_state = '10'

            order_id.after_done_state = 'refunded'
            return super(ReturnPicking, self).create_returns()


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    after_done_state = [
        ('1', u'仅退货'),
        ('2', u'仅退款'),
        ('3', u'退货退款'),
        ('4', u'已退货'),
        ('5', u'已退款'),
        ('6', u'已退货退款'),
        ('7', u'拒绝退货'),
        ('8', u'拒绝退款'),
        ('9', u'拒绝退货退款'),
        ('10', u'已退货拒绝退款'),
        ('11', u'已退款拒绝退货'),
    ]
    after_done_state = fields.Selection(after_done_state, string=u'售后状态', readonly=True)
