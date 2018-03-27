# coding: utf-8
import logging, base64, hashlib, time
from lxml import etree
from suds.client import Client
from odoo.exceptions import UserError
from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class SendWizard(models.TransientModel):
    _inherit = "send.express.order"
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
    express_id = fields.Many2one('delivery.carrier', string=u"快递",
                                 default=lambda self: self.env.ref('sf_express.express_1'))
    express_order_type = fields.Selection(express_order_type, string=u"快件类型", default='1')
    payment_method = fields.Selection(payment_method, string=u"运费付款方式", default='1')
    tb_quantity = fields.Integer(string=u"包裹数量", default='1')

    def get_sender_info(self):
        Send_valus = self.picking_id.picking_type_id.warehouse_id
        j_county = Send_valus.partner_id.street
        j_city = Send_valus.partner_id.city
        j_address = Send_valus.partner_id.street2
        j_tel = Send_valus.partner_id.mobile
        j_company = Send_valus.partner_id.name
        j_province = Send_valus.partner_id.state_id.name
        data = {
            'j_company': j_company,
            'j_contact': j_company,
            'j_tel': j_tel,
            'j_mobile': '',
            'j_province': j_province,
            'j_city': j_city,
            'j_county': j_county,
            'j_address': j_address,
        }
        return data

    def make_express_data(self, order, sender_info):
        order_info = {
            'd_contact': order.partner_id.name or '',
            'd_tel': order.partner_id.phone or '',
            'd_mobile': order.partner_id.mobile or '',
            'd_address': str(
                order.partner_id.state_id.name + order.partner_id.city + order.partner_id.street) or '',
            'd_company': u'顺丰速运',
            'express_type': self.express_order_type,
            'pay_method': self.payment_method,
            'parcel_quantity': str(self.tb_quantity),
            'remark': '',
        }
        if order.order_number:
            order_info.update({
                'orderid': order.order_number,
            })
        else:
            order_info.update({
                'orderid': order.name,
            })

        if self.payment_method == '1':
            order_info.update({
                'custid': self.express_id.custid
            })

        order_info.update(sender_info)
        # 下单报文信息
        xml_str = "<Request service='OrderService' lang='zh-CN'><Head>%s</Head><Body/></Request>" % self.express_id.bsp_head
        root_node = etree.fromstring(xml_str)
        order_node = etree.Element('Order')
        root_node.find('Body').append(order_node)
        for k, v in order_info.items():
            order_node.set(k, v)

        # 设置运输物品
        for order_line in order.move_lines:
            cargo_node = etree.Element('Cargo')
            cargo_node.set('name', order_line.product_id.name)
            cargo_node.set('count', str(order_line.product_uom_qty))
            order_node.append(cargo_node)

        # 货到付款
        if u"货到付款" in order.sale_id.payment_term_id.name:
            order_node.append(etree.fromstring("<AddedService name='COD' value='%s'/>" % (self.express_id.custid)))
            if order.sale_id.amount_total >= 1000:  # 代收大于等于1000元保价
                # 保价
                order_node.append(
                    etree.fromstring("<AddedService name='INSURE' value='%s'/>" % order.sale_id.amount_total))
        else:
            if order.sale_id.amount_total >= 1800:  # 代收大于等于1000元保价
                # 保价
                order_node.append(
                    etree.fromstring("<AddedService name='INSURE' value='%s'/>" % order.sale_id.amount_total))

        # 发送数据
        xml_str = etree.tostring(root_node, xml_declaration=True, encoding='UTF-8').decode('utf-8')
        verify_code = base64.b64encode(
            hashlib.md5((xml_str + self.express_id.checkword).encode("utf-8")).digest())
        return xml_str, verify_code

    def confirm(self):
        super(SendWizard, self).confirm()
        if not self.picking_id or self.api != '2':
            return
        sender_info = self.get_sender_info()
        client = Client(self.express_id.url)
        print('sf_express')
        # 依次发送各订单信息
        for order in self.picking_id:
            if order.state == 'done' or order.picking_type_code != 'outgoing' or order.is_send:
                raise UserError('该订单：%s.已出库或该订单不是出库单' % order.name)
            xml_str, verify_code = self.make_express_data(order, sender_info)
            # 处理响应
            resp_unicode = client.service.sfexpressService(xml_str, verify_code.decode())
            resp_node = etree.fromstring(resp_unicode.encode('utf-8'))
            if resp_node.xpath('//Head')[0].text != 'OK':
                err = resp_node.xpath('//ERROR')[0]
                log_str = u'%s发货失败: [%s], %s' % (order.name, err.get('code'), err.text)
                order.faild_log = log_str  # 记录发货失败原因
                order.order_number = int(int(round(time.time() * 1000)))  # 发货失败时，修正订单号
                _logger.error(log_str)
            else:
                info = resp_node.xpath('//OrderResponse')[0]
                mailno = info.get('mailno')  # 顺丰运单
                orderid = info.get('orderid=')  # 订单号
                origincode = info.get('origincode')  # 原寄地区域代码，可用于顺丰电子运单标签打印。
                destcode = info.get('destcode')  # 目的地区域代码，可用于顺丰电子运单标签打印。
                filter_result = info.get("filter_result")
                # 更新发货信息
                sql = "update stock_picking set carrier_tracking_ref=%s,origincode=%s,destcode=%s,filter_result=%s,is_send=TRUE," \
                      "payment_method=%s,express_order_type=%s,faild_log='',carrier_id=%s where id=%s OR order_number=%s"
                self._cr.execute(sql, (
                    mailno, origincode, destcode, filter_result, self.payment_method, self.express_order_type,
                    self.express_id.id, order.id, orderid))
                # 增加物流信息
                query = "insert into print_order(carrier_id,name,mailno,origincode,destcode,filter_result,payment_method,express_order_type,print_num)" \
                        " VALUES (%s,%s,%s,%s,%s,%s,%s,%s,0)"
                self._cr.execute(query, (
                    self.express_id.id, order.id, mailno, origincode, destcode, filter_result, self.payment_method,
                    self.express_order_type))
