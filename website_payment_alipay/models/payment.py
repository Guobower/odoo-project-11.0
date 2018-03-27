# coding: utf-8


import logging
from . import func
from odoo.addons.website_payment_alipay.controllers import main
import json
from urllib.parse import urljoin
import urllib
from odoo import api, fields, models, _
from odoo.addons.payment.models.payment_acquirer import ValidationError
from odoo.addons.website_payment_alipay.controllers.main import AlipayController
from odoo.tools.float_utils import float_compare

_logger = logging.getLogger(__name__)


class AcquirerAlipay(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(selection_add=[('alipay', 'Alipay')])
    alipay_partner = fields.Char('Alipay Partner ID', required_if_provider="alipay", groups='base.group_user')
    alipay_seller_id = fields.Char('Alipay Seller ID', groups='base.group_user')
    alipay_private_key = fields.Text('Alipay Private KEY', groups='base.group_user')
    alipay_public_key = fields.Text('Alipay Public key', groups='base.group_user')
    alipay_sign_type = fields.Char('Sign Type', default='RSA', groups='base.gruop_user')
    alipay_transport = fields.Selection([
        ('https', 'HTTPS'),
        ('http', 'HTTP')], groups='base.group_user')
    alipay_service = fields.Char('Service', required_if_provider="alipay", groups='base.group_user',
                                 default='create_direct_pay_by_user')
    alipay_payment_type = fields.Char('Payment Type', groups='base.group_user', default='1')

    def _get_feature_support(self):
        """Get advanced feature support by provider.

        Each provider should add its technical in the corresponding
        key for the following features:
            * fees: support payment fees computations
            * authorize: support authorizing payment (separates
                         authorization and capture)
            * tokenize: support saving payment data in a payment.tokenize
                        object
        """
        res = super(AcquirerAlipay, self)._get_feature_support()
        res['fees'].append('weixin')
        return res

    @api.model
    def _get_alipay_urls(self, environment):
        """ Alipay URLS """
        if environment == 'prod':
            return {
                'alipay_form_url': 'https://mapi.alipay.com/gateway.do?',
            }
        else:
            return {
                'alipay_form_url': 'https://openapi.alipay.com/gateway.do?',
            }

    @api.multi
    def alipay_compute_fees(self, amount, currency_id, country_id):
        """ Compute Alipay fees.

            :param float amount: the amount to pay
            :param integer country_id: an ID of a res.country, or None. This is
                                       the customer's country, to be compared to
                                       the acquirer company country.
            :return float fees: computed fees
        """
        if not self.fees_active:
            return 0.0
        country = self.env['res.country'].browse(country_id)
        if country and self.company_id.country_id.id == country.id:
            percentage = self.fees_dom_var
            fixed = self.fees_dom_fixed
        else:
            percentage = self.fees_int_var
            fixed = self.fees_int_fixed
        fees = (percentage / 100.0 * amount + fixed) / (1 - percentage / 100.0)
        return fees

    @api.multi
    def alipay_form_generate_values(self, values):

        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')

        alipay_tx_values = dict(values)
        alipay_tx_values.update({
            # basic parameters
            'service': self.alipay_service,
            'partner': self.alipay_partner,
            '_input_charset': 'utf-8',
            'sign_type': self.alipay_sign_type,
            'return_url': '%s' % urljoin(base_url, AlipayController._return_url),
            'notify_url': '%s' % urljoin(base_url, AlipayController._notify_url),
            'out_trade_no': values['reference'],
            'subject': '%s: %s' % (self.company_id.name, values['reference']),
            'payment_type': '1',
            'total_fee': values['amount'],
            'seller_id': self.alipay_seller_id,
            'seller_email': self.alipay_seller_id,
            'seller_account_name': self.alipay_seller_id,
            'body': '测试',
        })
        subkey = ['service', 'partner', '_input_charset', 'return_url', 'notify_url', 'out_trade_no', 'subject',
                  'payment_type', 'total_fee', 'seller_id', 'body']
        need_sign = {key: alipay_tx_values[key] for key in subkey}
        params, sign = func.buildRequestMysign(need_sign, self.alipay_private_key)
        alipay_tx_values.update({
            'sign': sign,
        })
        return alipay_tx_values

    @api.multi
    def alipay_get_form_action_url(self):
        return self._get_alipay_urls(self.environment)['alipay_form_url']


class TxAlipay(models.Model):
    _inherit = 'payment.transaction'

    alipay_txn_type = fields.Char('Transaction type')

    # --------------------------------------------------
    # FORM RELATED METHODS
    # --------------------------------------------------

    @api.model
    def _alipay_form_get_tx_from_data(self, data):
        reference, txn_id = data.get('out_trade_no'), data.get('trade_no')
        if not reference or not txn_id:
            error_msg = _('Alipay: received data with missing reference (%s) or txn_id (%s)') % (reference, txn_id)
            _logger.info(error_msg)
            raise ValidationError(error_msg)

        txs = self.env['payment.transaction'].search([('reference', '=', reference)])
        if not txs or len(txs) > 1:
            error_msg = 'Alipay: received data for reference %s' % (reference)
            if not txs:
                error_msg += '; no order found'
            else:
                error_msg += '; multiple order found'
            _logger.info(error_msg)
            raise ValidationError(error_msg)
        return txs[0]

    @api.multi
    def _alipay_form_get_invalid_parameters(self, data):
        invalid_parameters = []
        return invalid_parameters

    @api.multi
    def _alipay_form_validate(self, data):
        status = data.get('trade_status')
        res = {
            'acquirer_reference': data.get('out_trade_no'),
            'alipay_txn_type': data.get('payment_type'),
            'acquirer_reference': data.get('trade_no'),
            'partner_reference': data.get('buyer_id')
        }
        if status in ['TRADE_FINISHED', 'TRADE_SUCCESS']:
            _logger.info('Validated alipay payment for tx %s: set as done' % (self.reference))
            res.update(state='done', date_validate=data.get('gmt_payment', fields.datetime.now()))
            return self.write(res)
        else:
            error = 'Received unrecognized status for Alipay payment %s: %s, set as error' % (self.reference, status)
            _logger.info(error)
            res.update(state='error', state_message=error)
            return self.write(res)

    @api.multi
    def action_returns_commit(self):
        # ==================
        # 确认退款操作
        # ==================
        url = 'https://openapi.alipay.com/gateway.do'
        data = {
            'out_trade_no': self.reference,
            'trade_no': self.acquirer_reference,
            'refund_amount': self.reference,
            'refund_reason': '正常退款',
            'out_trade_no': self.reference,
            'out_trade_no': self.reference,
        }
        request_data = urllib.request.Request(url, data)
        result = urllib.request.urlopen(request_data).read()
        json_result = json.dumps(result)
        refund_response = json_result['alipay_trade_refund_response']
        if refund_response['msg'] == 'Success':
            res = {
                'sign': refund_response['sign'],
                'trade_no': refund_response['trade_no'],
                'out_trade_no': refund_response['out_trade_no'],
                'refund_fee': refund_response['refund_fee'],
                'gmt_refund_pay': refund_response['gmt_refund_pay'],
                'sign_type': "RSA",
            }
            isSign = main.getSignVeryfy(res)

            res = self.env['payment.transaction'].sudo().search(
                [('acquirer_reference', '=', refund_response['trade_no']),
                 ('reference', '=', refund_response['out_trade_no'])])
            if isSign and res:
                super(TxAlipay, self).action_returns_commit()
        else:
            raise ValidationError("%s, %s" % (refund_response['sub_code'], refund_response['sub_msg']))
