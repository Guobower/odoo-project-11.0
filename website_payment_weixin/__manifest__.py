# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# Auth: Gavin GU Email:guwenfengvip@163.com

{
    'name': '微信支付',
    'category': 'Website',
    'summary': '微信支付',
    'version': '11.1.0',
    'description': """商城微信支付""",
    'author': "Gavin Gu",
    'website': "",
    'depends': ['payment', 'website_payment_return'],
    'data': [
        'templates/payment_weixin_templates.xml',
        'data/weixin.xml',
        'views/payment_acquirer.xml',

    ],
    'installable': True,
}
