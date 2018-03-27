# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# Auth: Gavin GU Email:guwenfengvip@163.com
{
    'name': '支付宝支付',
    'author': "Gavin Gu",
    'website': "",
    'category': 'Accounting',
    'summary': '支付宝支付',
    'version': '1.0',
    'description': """支付宝支付 """,
    'depends': ['payment', 'website_payment_return'],
    'data': [
        'templates/payment_alipay_templates.xml',
        'data/payment_acquirer_data.xml',
        'views/payment_views.xml',
    ],
    "external_dependencies": {
        "python": ["Crypto"],
    },
    'installable': True,

}
