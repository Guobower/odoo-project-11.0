# -*- coding: utf-'8' "-*-"
from odoo.addons.website_payment_weixin.controllers.controllers import WeixinController

import socket

import json
from urllib.parse import urljoin
import logging
import urllib

from lxml import etree
import random
import string, datetime, time
from . import util
from odoo.addons.payment.models.payment_acquirer import ValidationError
from odoo.http import request
from odoo import api, fields, models

_logger = logging.getLogger(__name__)


def random_generator(size=32, chars=string.ascii_uppercase + string.digits):
    return ''.join([random.choice(chars) for n in range(size)])


class AcquirerWeixin(models.Model):
    _inherit = 'payment.acquirer'

    def _get_ipaddress(self):
        hostname = socket.gethostname()
        ip = '127.0.0.1'
        return ip

    provider = fields.Selection(selection_add=[('weixin', 'weixin')])
    weixin_appid = fields.Char(string='Weixin APPID', required_if_provider='weixin')
    weixin_mch_id = fields.Char(string=u'微信支付商户号', required_if_provider='weixin')
    weixin_key = fields.Char(string=u'API密钥 ', required_if_provider='weixin')
    weixin_secret = fields.Char(string='Weixin Appsecret', required_if_provider='weixin')

    def _get_weixin_urls(self, environment):
        if environment == 'prod':
            return {
                'weixin_url': 'https://api.mch.weixin.qq.com/pay/unifiedorder'
            }
        else:
            return {
                'weixin_url': 'https://api.mch.weixin.qq.com/pay/unifiedorder'
            }

    @api.one
    def _get_weixin_key(self):
        return self.weixin_key

    _defaults = {
        'fees_active': False,
    }

    def json2xml(self, json):
        string = ""
        for k, v in json.items():
            string = string + "<%s>" % (k) + str(v) + "</%s>" % (k)

        return string

    def _try_url(self, request, tries=3):
        done, res = False, None
        while (not done and tries):
            try:
                res = urllib.request.urlopen(request)
                done = True
            except urllib.HTTPError as e:
                res = e.read()
                e.close()
                if tries and res and json.loads(res)['name'] == 'INTERNAL_SERVICE_ERROR':
                    _logger.warning('Failed contacting Paypal, retrying (%s remaining)' % tries)
            tries = tries - 1
        if not res:
            pass
        result = res.read()
        res.close()
        return result

    def get_wx_appid(self):

        return self.wx_appid,

    @api.multi
    def weixin_form_generate_values(self, tx_values):
        self.ensure_one()
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        amount = int(tx_values.get('amount', 0) * 100)
        nonce_str = random_generator()
        data_post = {}
        now_time = time.strftime('%Y%m%d%H%M%S')
        data_post.update(
            {
                'appid': self.weixin_appid,
                'body': tx_values['reference'],
                'mch_id': self.weixin_mch_id,
                'nonce_str': nonce_str,
                'notify_url': '%s' % urljoin(base_url, WeixinController._notify_url),
                'openid': 'oUpF8uMuAJO_M2pxb1Q9zNjWeS6o',
                'out_trade_no': now_time,
                'spbill_create_ip': self._get_ipaddress(),
                'total_fee': amount,
                'trade_type': 'JSAPI',
            }
        )

        _, prestr = util.params_filter(data_post)
        sign = util.build_mysign(prestr, self.weixin_key, 'MD5')
        data_post['sign'] = sign

        # data_xml = "<xml>" + self.json2xml(data_post) + "</xml>"
        # url = self._get_weixin_urls(self.environment)['weixin_url']
        # # print(data_xml)
        # request_data = urllib.request.Request(url, data_xml.encode(encoding='utf-8'))
        # result = urllib.request.urlopen(request_data).read()
        # # # result = self._try_url(request, tries=3)
        # print(result)
        # data_post.update({
        #     # 'data_xml': data_xml,
        #     'tx_url': url,
        # })
        # return_xml = etree.fromstring(result)
        # if return_xml.find('return_code').text == "SUCCESS" and return_xml.find('code_url').text != False:
        #     qrcode = return_xml.find('code_url').text
        #     data_post.update({
        #         'qrcode': qrcode,
        #     })
        # else:
        #     return_code = return_xml.find('return_code').text
        #     return_msg = return_xml.find('return_msg').text
        #     raise ValidationError("%s, %s" % (return_code, return_msg))
        print(data_post)
        tx_values = data_post
        return tx_values

    @api.multi
    def weixin_get_form_action_url(self):
        self.ensure_one()
        return self._get_weixin_urls(self.environment)['weixin_url']


class TxWeixin(models.Model):
    _inherit = 'payment.transaction'

    weixin_txn_id = fields.Char(string='Transaction ID')
    weixin_txn_type = fields.Char(string='Transaction type')

    # --------------------------------------------------
    # FORM RELATED METHODS
    # --------------------------------------------------
    # 付款交易订单查询是否存在
    def _weixin_form_get_tx_from_data(self, data):
        reference, txn_id = data.get('out_trade_no'), data.get('out_trade_no')
        if not reference or not txn_id:
            error_msg = 'weixin: received data with missing reference (%s) or txn_id (%s)' % (reference, txn_id)
            _logger.error(error_msg)
            raise ValidationError(error_msg)

        # find tx -> @TDENOTE use txn_id ?
        tx_ids = self.search([('acquirer_reference', '=', reference)])
        if not tx_ids or len(tx_ids) > 1:
            error_msg = 'weixin: received data for reference %s' % (reference)
            if not tx_ids:
                error_msg += '; no order found'
            else:
                error_msg += '; multiple order found'
            _logger.error(error_msg)
            raise ValidationError(error_msg)
        return tx_ids[0]

    # #付款交易金额检查--交易币种检查
    # def _weixin_form_get_invalid_parameters(self, data):
    #     invalid_parameters = []
    #
    #     if float_compare(float(data.get('total_fee', '0.0')), self.amount, 2) != 0:
    #         invalid_parameters.append(('amount', data.get('total_fee'), '%.2f' % self.amount))
    #     if data.get('fee_type') != self.currency_id.name:
    #         invalid_parameters.append(('currency', data.get('fee_type'), self.currency_id.name))
    #
    #     return invalid_parameters

    def _weixin_form_validate(self, data):
        status = data.get('trade_state')
        data = {
            'acquirer_reference': data.get('transaction_id'),
            'weixin_txn_id': data.get('transaction_id'),
            'weixin_txn_type': data.get('fee_type'),
        }

        if status == 'SUCCESS':
            _logger.info('Validated weixin payment for tx %s: set as done' % (self.reference))
            data.update(state='done', date_validate=data.get('time_end', fields.datetime.now()))
            return self.write(data)

        else:
            error = 'Received unrecognized status for weixin payment %s: %s, set as error' % (self.reference, status)
            _logger.info(error)
            data.update(state='error', state_message=error)
            return self.write(data)

    @api.multi
    def action_returns_commit(self):
        # ==================
        # 确认退款操作
        # ==================
        data = {
            'appid', self.acquirer_id.appid,
            'mch_id', self.acquirer_id.mch_id,
            'nonce_str', random_generator(),
            'out_refund_no', self.reference,
            'refund_fee', int(self.amount * 100),
            'total_fee', int(self.amount * 100),
            'transaction_id', self.acquirer_reference,

        }
        _, prestr = util.params_filter(data)
        sign = util.build_mysign(prestr, self.acquirer_id.weixin_key, 'MD5')
        data.update({'sign': sign})

        data_xml = "<xml>" + self.json2xml(data) + "</xml>"
        url = 'https://api.mch.weixin.qq.com/secapi/pay/refund'
        # print(data_xml)
        request_data = urllib.request.Request(url, data_xml.encode(encoding='utf-8'))
        result = urllib.request.urlopen(request_data).read()
        return_xml = etree.fromstring(result)
        if return_xml.find('return_code').text == "SUCCESS" and return_xml.find('sign').text != False:
            transaction_id = return_xml.find('transaction_id').text
            out_refund_no = return_xml.find('out_refund_no').text
            sign = return_xml.find('sign').text
            res = self.env['payment.transaction'].sudo().search(
                [('acquirer_reference', '=', transaction_id), ('reference', '=', out_refund_no)])
            if res:
                super(TxWeixin, self).action_returns_commit()
        else:
            return_code = return_xml.find('return_code').text
            return_msg = return_xml.find('return_msg').text
            raise ValidationError("%s, %s" % (return_code, return_msg))
