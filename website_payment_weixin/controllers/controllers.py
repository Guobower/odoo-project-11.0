# -*- coding: utf-8 -*-

import logging
from lxml import etree
from odoo import http, SUPERUSER_ID
from odoo.http import request
import urllib, json
from odoo.addons.website_payment_weixin.models import util

_logger = logging.getLogger(__name__)


class WeixinController(http.Controller):
    _notify_url = '/payment/weixin/notify'

    def weixin_validate_data(self, post):

        # 方式一 解析返回信息
        json_data = {}
        for el in etree.fromstring(str(post)):
            json_data[el.tag] = el.text

        _logger.info("微信返回信息-----json： %s" % (json_data))
        _KEY = request.registry['payment.acquirer']._get_weixin_key()
        _, prestr = util.params_filter(json_data)
        mysign = util.build_mysign(prestr, _KEY, 'MD5')
        if mysign != json_data.get('sign'):
            return 'false'

        _logger.info('weixin: validated data')
        return request.env['payment.transaction'].sudo().form_feedback(json_data, 'weixin')

    @http.route('/payment/weixin/notify', type='http', auth='public', methods=['POST'], csrf=False)
    def weixin_notify(self, **post):
        _logger.info("微信返回信息： %s" % (post))
        if self.weixin_validate_data(post):
            return 'success'
        else:
            return ''

    # 网页授权验证结束接口
    @http.route(['/wx_verify'], type="http", auth='none', methods=['GET', 'POST'], csrf=False)
    def wx_verify(self, **kwargs):
        # 网页授权完毕，进行获取用户信息验证，验证结束登陆到对应的网站
        if kwargs:
            res_users = self.get_token(kwargs)
            openid = res_users['openid']
            return openid
        else:
            # 触发微信返回code码
            url = self.check_url
            # Header("Location: " + url);
            exit();

    def send_url(self, token_url, params):
        try:
            data = urllib.parse.urlencode(params).encode('utf-8')
            req = urllib.request.Request(token_url, data=data)
            get_data = urllib.request.urlopen(req).read().decode('utf-8')
            sort_data = json.loads(get_data)

            return sort_data
        except Exception:
            _logger.info("获取参数错误：")

    # 微信用户授权地址
    def check_url(self):
        self.wx_appid = request.env['payment.acquirer'].sudo().get_wx_appid()
        redirect_uri = self.env['ir.config_parameter'].get_param('web.base.url') + '/wx_verify'
        url = 'https://open.weixin.qq.com/connect/oauth2/authorize?appid=' + self.wx_appid + '&' \
              + redirect_uri + '&response_type=code&scope=snsapi_base&state=wx_verify#wechat_redirect'
        return url

    # 通过code换取网页授权access_token
    def get_token(self, res_code):

        token_url = u'https://api.weixin.qq.com/sns/oauth2/access_token'
        params = {
            'appid': self.wx_appid,
            'secret': self.wx_AppSecret,
            'code': res_code['code'],
            'grant_type': 'authorization_code'
        }
        return self.send_url(token_url, params)

    # 网页授权
    @http.route('/wx_verify/MP_verify_l1JijRgASh5SDh0Q.txt', type='http', auth="none", methods=['GET', 'POST'],
                csrf=False)
    def wx_lweb(self, **kw):
        _logger.info("读取文件夹")
        return 'l1JijRgASh5SDh0Q'
