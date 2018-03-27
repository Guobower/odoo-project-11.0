# coding: utf-8

from odoo import models, fields, api

import logging

_logger = logging.getLogger(__name__)


class PrintOrder(models.Model):
    _name = 'print.order'
    _description = u"发货信息表"
    # 订单信息
    name = fields.Many2one('stock.picking', string=u'订单号')

    express_order_type = [
        ('1', u'顺丰标快'),
        ('2', u'顺丰特惠'),
        ('5', u'顺丰次晨'),
        ('6', u'顺丰即日'),
        ('37', u'云仓专配次日'),
        ('38', u'云仓转配隔日'),
    ]

    payment_method = [
        ('1', u'寄付月结'),
        ('4', u'寄付现结'),
        ('2', u'到付'),
        ('3', u'第三方付'),
    ]

    # 快递信息
    carrier_id = fields.Many2one('delivery.carrier', string=u'快递')
    mailno = fields.Char(string=u'运单号')
    origincode = fields.Char(string=u"原寄地区域代码")
    destcode = fields.Char(string=u"目的地区域代码")
    filter_result = fields.Selection([('1', u'人工确认'), ('2', u'可收派'), ('3', u'不可以收派')], string=u'筛单结果')
    is_print = fields.Boolean(string=u"已打印")
    remark = fields.Char(string=u"备注")
    info_id = fields.One2many('stock.logistics', compute='compute_info_id', string=u'快递信息')
    payment_method = fields.Selection(payment_method, string=u"运费付款方式", default='1')
    express_order_type = fields.Selection(express_order_type, string=u"快件类型", default='1')
    print_num = fields.Integer(string=u"打印次数", default=0)

    def compute_info_id(self):
        for res in self:
            res.info_id = self.name.logistics_id

    @api.model
    def get_json_data(self, order):
        print_order = self.env['print.order'].sudo().search([('id', 'in', order)])
        listjson = []
        for res in print_order:
            Send_valus = res.name.picking_id.picking_type_id.warehouse_id
            j_county = Send_valus.partner_id.street
            j_city = Send_valus.partner_id.city
            j_address = Send_valus.partner_id.street2
            j_tel = Send_valus.partner_id.mobile
            j_company = Send_valus.partner_id.name
            j_province = Send_valus.partner_id.state_id.name

            listStr = '%s%s%s%s' % (j_province, j_city, j_county, j_address)
            strSendMessage = '%s %s %s' % (j_company, j_company, j_tel)
            data = {
                'strExpresstype': res.express_order_type,  # 顺丰业务类型
                'strMailID': res.mailno,  # 条码物流单号
                'strName': res.name.receiver,  # 收货人
                'strDestcode': res.destcode,  # 目的地址代码
                'strPhone': res.name.receiver_phone,  # 收货电话
                'strAddress': res.name.receiver_address,  # 收货地址
                'strPaymount': res.name.amount_total,  # 代收金额
                'strProduct': "",  # 产品
                'strPayMethod': res.payment_method,  # 顺丰付款方式
                'strSendMessage': strSendMessage,  # 顺丰付款方式
                'strSendaddres': listStr,  # 地址
                'SFMonthlyAccount': u'月结账号:%s' % res.name.carrier_id.custid,
                'dai_proprice': res.name.carrier_id.dai_proprice,
                'proprice': res.name.carrier_id.proprice,
            }
            listjson.append(data)

        return listjson

    @api.model
    def print_done(self, order):
        up_query = "update print_order set is_print=TRUE,print_num=print_num+1 where id in %s"
        self._cr.execute(up_query, (tuple(order),))
