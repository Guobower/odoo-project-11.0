# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    is_send = fields.Boolean(string=u"已发货", copy=False)
    logistics_id = fields.One2many('stock.logistics', 'picking_id', string='logistics info')

    def button_validate(self):
        if self.is_send or self.picking_type_code != 'outgoing':
            return super(StockPicking, self).button_validate()
        else:
            raise UserError('还未发货，不允许验证订单')

    @api.multi
    def send_to_shipper(self):
        self.ensure_one()
        # 取消标准发货方式
        res = self.carrier_id.send_shipping(self)[0]
        self.carrier_price = res['exact_price']
        # self.carrier_tracking_ref = res['tracking_number']
        order_currency = self.sale_id.currency_id or self.company_id.currency_id
        msg = _(" 发货方式:%s . 快递单号: %s<br/>邮费: %s %s") % (
            self.carrier_id.name, self.carrier_tracking_ref, self.carrier_price, order_currency.name)
        self.message_post(body=msg)

    def open_website_url(self):
        pass


class StockLogistics(models.Model):
    _name = 'stock.logistics'

    _order = "date desc"

    name = fields.Char(string=u'地点')
    date = fields.Datetime(string=u'时间')
    description = fields.Char(string='描述')
    picking_id = fields.Many2one('stock.picking', 'logistics_id')


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    api = fields.Selection([('1', u'第三方'), ('2', u'直接对接')], string='接口类型')
