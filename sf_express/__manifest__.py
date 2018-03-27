# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# Auth: Gavin GU Email:guwenfengvip@163.com
{
    'name': "sf_express",

    'summary': """
            顺丰发货
        """,

    'description': """
        针对已审核的订单进行物流选择发货
        顺丰：利用API获取快递单号，然后进行热敏打印面单
        物流查询，物流追踪、物流异常备注
    """,

    'author': "Gavin GU",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'stock',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock_logistics'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/delivery_data.xml',
        'views/express_delivery_view.xml',
        'views/express_order_views.xml',
        'views/print_order_view.xml',
        'views/templates.xml',
        'wizard/express_wizard_views.xml',

    ],
    # only loaded in demonstration mode

    'qweb': ['static/src/xml/*.xml'],
    'application': True,
    "external_dependencies": {
        "python": ['suds'],
    },

    'demo': [
        'demo/demo.xml',
    ],
}
