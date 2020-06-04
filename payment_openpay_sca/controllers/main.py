# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
import pprint
import werkzeug

from odoo.http import route, request
from odoo.addons.payment_openpay.controllers.main import OpenpayController

_logger = logging.getLogger(__name__)


class OpenpayControllerSCA(OpenpayController):
    _success_url = '/payment/openpay/success'
    _cancel_url = '/payment/openpay/cancel'

    @route(['/payment/openpay/success', '/payment/openpay/cancel'], type='http', auth='public')
    def openpay_success(self, **kwargs):
        request.env['payment.transaction'].sudo().form_feedback(kwargs, 'openpay')
        return werkzeug.utils.redirect('/payment/process')

    @route(['/payment/openpay/s2s/create_json_3ds'], type='json', auth='public', csrf=False)
    def openpay_s2s_create_json_3ds(self, verify_validity=False, **kwargs):
        if not kwargs.get('partner_id'):
            kwargs = dict(kwargs, partner_id=request.env.user.partner_id.id)
        token = request.env['payment.acquirer'].browse(int(kwargs.get('acquirer_id'))).with_context(openpay_manual_payment=True).s2s_process(kwargs)

        if not token:
            res = {
                'result': False,
            }
            return res

        res = {
            'result': True,
            'id': token.id,
            'short_name': token.short_name,
            '3d_secure': False,
            'verified': False,
        }

        if verify_validity != False:
            token.validate()
            res['verified'] = token.verified

        return res

    @route('/payment/openpay/s2s/create_setup_intent', type='json', auth='public', csrf=False)
    def openpay_s2s_create_setup_intent(self, acquirer_id, **kwargs):
        acquirer = request.env['payment.acquirer'].browse(int(acquirer_id))
        res = acquirer.with_context(openpay_manual_payment=True)._create_setup_intent(kwargs)
        return res.get('client_secret')


    @route('/payment/openpay/s2s/process_payment_intent', type='json')
    def openpay_s2s_process_payment_intent(self, **post):
        return request.env['payment.transaction'].sudo().form_feedback(post, 'openpay')

    
    # These routes are deprecated, let's remove them for security's sake
    def openpay_s2s_create_json(self, **post):
        raise werkzeug.exceptions.NotFound()
    
    def openpay_s2s_create(self, **post):
        raise werkzeug.exceptions.NotFound()

    def openpay_create_charge(self, **post):
        raise werkzeug.exceptions.NotFound()
