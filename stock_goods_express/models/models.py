# -*- coding: utf-'8' "-*-"

from odoo import api, fields, models
from odoo.exceptions import UserError


class StickPicking(models.Model):
    _inherit = 'stock.picking'

    def open_website_url(self):
        super(StickPicking, self).open_website_url()
        if self.carrier_tracking_ref and self.carrier_id.api == '1':
            json_str = self.env['stock.goods.express'].recognise(self.id)
            print(json_str)
            if json_str['Success'] == True and json_str['Traces']:
                message = json_str['Traces']
                if message:
                    # Delete history recodes
                    self._cr.execute("delete from stock_logistics where picking_id=%s" % self.id)
                    for list in message:
                        date = list['AcceptTime']
                        description = list['AcceptStation'],
                        query = "insert into stock_logistics (date,description,picking_id) VALUES (%s,%s,%s)"
                        self._cr.execute(query, (date, description, self.id))
            else:
                raise UserError(u'警告:' + json_str['Reason'])


class Delivery(models.Model):
    _inherit = 'delivery.carrier'

    code = fields.Char(string="承运商代码")
    CustomerName = fields.Char(string="面单账号")
    CustomerPwd = fields.Char(string="面单密码")
