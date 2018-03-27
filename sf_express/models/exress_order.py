# coding: utf-8

import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from suds.client import Client
import base64, hashlib
from odoo.exceptions import AccessError
from lxml import etree

_logger = logging.getLogger(__name__)


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    bsp_head = fields.Char(string=u'客户号')
    checkword = fields.Char(string=u'秘钥')
    custid = fields.Char(string=u'月结卡号')
    url = fields.Char(string=u"请求地址")
    proprice = fields.Float(string=u"保价金额(非代收)")
    dai_proprice = fields.Float(string=u"保价金额(代收)")


class ExpressOrder(models.Model):
    _inherit = 'stock.picking'

    # 订单信息
    order_number = fields.Char(string=u"修正订单号", help=u'用于发货失败，修正订单号再次发货', copy=False)
    # 发货失败原因
    faild_log = fields.Char(string=u'发货失败信息', copy=False)
    # 快递信息
    payment_method = [
        ('1', u'寄付月结'),
        ('4', u'寄付现结'),
        ('2', u'到付'),
        ('3', u'第三方付'),
    ]
    express_order_type = [
        ('1', u'顺丰标快'),
        ('2', u'顺丰特惠'),
        ('5', u'顺丰次晨'),
        ('6', u'顺丰即日'),
        ('37', u'云仓专配次日'),
        ('38', u'云仓转配隔日'),
    ]
    origincode = fields.Char(string=u"原寄地区域代码", copy=False)
    destcode = fields.Char(string=u"目的地区域代码", copy=False)
    filter_result = fields.Selection([('1', u'人工确认'), ('2', u'可收派'), ('3', u'不可以收派')], string=u'筛单结果', copy=False)
    payment_method = fields.Selection(payment_method, string=u"运费付款方式", default='1')
    express_order_type = fields.Selection(express_order_type, string=u"快件类型", default='1')

    def open_website_url(self):
        super(ExpressOrder, self).open_website_url()
        if self.carrier_tracking_ref and self.carrier_id.api == '2' and self.carrier_id == self.env.ref(
                'sf_express.express_1').id:
            xml_str = """
                          <Request service='RouteService' lang='zh-CN'>
                          <Head>%s</Head>
                           <Body>
                          </Body>
                          </Request>
                      """ % (self.carrier_id.bsp_head)
            root_node = etree.fromstring(xml_str)
            route_node = etree.Element('RouteRequest')
            route_node.set('tracking_type', '1')
            route_node.set('method_type', '1')
            route_node.set('tracking_number', self.carrier_tracking_ref)
            root_node.find('Body').append(route_node)
            xml_str = etree.tostring(root_node, xml_declaration=True, encoding='UTF-8').decode('utf-8')
            client = Client(self.carrier_id.url)
            verifyCode = base64.b64encode(hashlib.md5((xml_str + self.carrier_id.checkword).encode("utf-8")).digest())
            xmlStr = client.service.sfexpressService(xml_str, verifyCode.decode())
            resp_node = etree.fromstring(xmlStr.encode('utf-8'))
            if resp_node.xpath('//Head')[0].text != 'OK':
                err = resp_node.xpath('//ERROR')[0]
                _logger.info(err)
                raise AccessError(err.get('code') + ':' + err.text)
            else:
                info = resp_node.xpath('//Route')
                if info:
                    # Delete history recodes
                    self._cr.execute("delete from stock_logistics where picking_id=%s" % self.id)
                    for res in info:
                        date = res.get('accept_time')
                        name = res.get('accept_address')
                        description = res.get('remark')
                        query = "insert into stock_logistics (date,name,description,picking_id) VALUES (%s,%s,%s,%s)"
                        self._cr.execute(query, (date, name, description, self.id))
