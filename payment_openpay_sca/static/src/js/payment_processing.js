odoo.define('payment_openpay_sca.processing', function (require) {
    'use strict';

    var ajax = require('web.ajax');
    var rpc = require('web.rpc');
    var PaymentProcessing = require('payment.processing');

    return PaymentProcessing.include({
        init: function ()
        {
            this._super.apply(this, arguments);
            this._authInProgress = false;
        },

        _openpayAuthenticate: function (tx)
        {
            return rpc.query({
                route: '/payment/openpay/s2s/process_payment_intent',
                params: _.extend({}, tx.openpay_charge_id, { reference: tx.reference })
            });
        },

        processPolledData: function (transactions)
        {
            this._super.apply(this, arguments);

            for (var itx = 0; itx < transactions.length; itx++)
            {
                var tx = transactions[itx];

                // ---------- CORREGIR --------------
                if (tx.acquirer_provider === 'openpay' && /*tx.state === 'pending' && */ !this._authInProgress)
                {
                    this._authInProgress = true;
                    this._openpayAuthenticate(tx);
                }
            }
        }
    });
});