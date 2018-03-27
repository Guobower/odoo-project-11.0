# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# Auth: Gavin GU Email:guwenfengvip@163.com
{
    'name': "物流跟踪",

    'summary': """
        物流跟踪
        """,

    'description': """
       物流跟踪
    """,

    'author': "Gavin Gu",
    'website': "",

    'category': 'stock',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', 'delivery'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'wizard/stock_logistics_wizard_views.xml',
    ],
    # only loaded in demonstration mode
    'installable': True,
}
