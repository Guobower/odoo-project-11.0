# coding: utf-8
import os
import logging
import base64
import hashlib
import time
from lxml import etree
from suds.client import Client

from odoo import models, fields, api, exceptions

_logger = logging.getLogger(__name__)


class SendWizard(models.TransientModel):
    _name = "send.express.order"

    picking_id = fields.Many2many('stock.picking', string=u'发货订单',
                                  default=lambda self: self.env['stock.picking'].browse(
                                      self._context.get('active_ids')).ids)
    express_id = fields.Many2one('delivery.carrier', string=u"快递", required=True,
                                 default=lambda self: self.env.ref('sf_express.express_1'))

    api = fields.Selection([('1', u'第三方'), ('2', u'直接对接')], string='接口类型', related='express_id.api')

    def confirm(self):
        pass
