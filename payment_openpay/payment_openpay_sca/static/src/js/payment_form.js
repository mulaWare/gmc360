odoo.define('payment_openpay.payment_form', function (require) {
    "use strict";
    
    var ajax = require('web.ajax');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var Dialog = require('web.Dialog');
    var PaymentForm = require('payment.payment_form');
    
    var _t = core._t;
    
    PaymentForm.include({   
        //--------------------------------------------------------------------------
        // Private
        //--------------------------------------------------------------------------
    
        /**
         * called when clicking on pay now or add payment event to create token for credit card/debit card.
         *
         * @private
         * @param {Event} ev
         * @param {DOMElement} checkedRadio
         * @param {Boolean} addPmEvent
         */
        _createOpenpayURL: function (ev, $checkedRadio, addPmEvent)
        {
            var self = this;
            var button = null;

            if (ev.type === 'submit')
            {
                button = $(ev.target).find('*[type="submit"]')[0];
            }
            else
            {
                button = ev.target;
            }
            this.disableButton(button);

            var acquirerID = this.getAcquirerIdFromRadio($checkedRadio);
            var acquirerForm = this.$('#o_payment_add_token_acq_' + acquirerID);
            var inputsForm = $('input', acquirerForm);
            if (this.options.partnerId === undefined)
            {
                console.warn('payment_form: unset partner_id when adding new token; things could go wrong');
            }
    
            var formData = self.getFormData(inputsForm);
            var openpay = this.openpay;
            var card = this.openpay_card_element;
            if (card._invalid)
            {
                return;
            }

            return rpc.query({
                route: '/payment/openpay/s2s/create_setup_intent',
                params: {'acquirer_id': formData.acquirer_id}
            }).then(function (intent_secret)
            {
                // need to convert between ES6 promises and jQuery 2 deferred \o/
                return $.Deferred(function (defer)
                {
                    openpay.handleCardSetup(intent_secret, card).then(function (result)
                    {
                        defer.resolve(result);
                    });
                });

                }).then(function (result)
                {
                    if (result.error)
                    {
                        return $.Deferred().reject({"message": {"data": { "message": result.error.message}}});
                    }
                    else
                    {
                        _.extend(formData, { "payment_method": result.setupIntent.payment_method });

                        return rpc.query({
                            route: formData.data_set,
                            params: formData,
                        });
                    }

                }).then(function (result)
                {
                    if (addPmEvent)
                    {
                        if (formData.return_url)
                        {
                            window.location = formData.return_url;
                        }
                        else
                        {
                            window.location.reload();
                        }
                    }
                    else
                    {
                        $checkedRadio.val(result.id);
                        self.el.submit();
                    }

                }).fail(function (error, event)
                {
                    // if the rpc fails, pretty obvious
                    self.enableButton(button);
                    self.displayError(
                    _t('Unable to save card'),
                    _t("We are not able to add your payment method at the moment. ") + error.data.message);
            });
        },
        /**
         * called when clicking a Openpay radio if configured for s2s flow; instanciates the card and bind it to the widget.
         *
         * @private
         * @param {DOMElement} checkedRadio
         */
        _bindOpenpayCard: function ($checkedRadio) {
            var acquirerID = this.getAcquirerIdFromRadio($checkedRadio);
            var acquirerForm = this.$('#o_payment_add_token_acq_' + acquirerID);
            var inputsForm = $('input', acquirerForm);
            var formData = this.getFormData(inputsForm);
            var openpay = Openpay(formData.openpay_publishable_key);
            var element = openpay.elements();
            var card = element.create('card', {hidePostalCode: true});
            card.mount('#card-element');
            card.on('ready', function(ev) {
                card.focus();
            });
            card.addEventListener('change', function (event) {
                var displayError = document.getElementById('card-errors');
                displayError.textContent = '';
                if (event.error) {
                    displayError.textContent = event.error.message;
                }
            });
            this.openpay = openpay;
            this.openpay_card_element = card;
        },
        /**
         * destroys the card element and any openpay instance linked to the widget.
         *
         * @private
         */
        _unbindOpenpayCard: function () {
            if (this.openpay_card_element) {
                this.openpay_card_element.destroy();
            }
            this.openpay = undefined;
            this.openpay_card_element = undefined;
        },
        /**
         * @override
         */
        updateNewPaymentDisplayStatus: function () {
            var $checkedRadio = this.$('input[type="radio"]:checked');
    
            if ($checkedRadio.length !== 1) {
                return;
            }
            var provider = $checkedRadio.data('provider')
            if (provider === 'openpay') {
                // always re-init openpay (in case of multiple acquirers for openpay, make sure the openpay instance is using the right key)
                this._unbindOpenpayCard();
                if (this.isNewPaymentRadio($checkedRadio)) {
                    this._bindOpenpayCard($checkedRadio);
                }
            }
            return this._super.apply(this, arguments);
        },
    
        //--------------------------------------------------------------------------
        // Handlers
        //--------------------------------------------------------------------------
    
        /**
         * @override
         */
        payEvent: function (ev) {
            ev.preventDefault();
            var $checkedRadio = this.$('input[type="radio"]:checked');
    
            // first we check that the user has selected a openpay as s2s payment method
            if ($checkedRadio.length === 1 && $checkedRadio.data('provider') === 'openpay' && this.isNewPaymentRadio($checkedRadio)) // Si es Openpay
            {
                return this._createOpenpayURL(ev, $checkedRadio);
            }
            else // Si no es Openpay
            {
                return this._super.apply(this, arguments);
            }
        },
        /**
         * @override
         */
        addPmEvent: function (ev) {
            ev.stopPropagation();
            ev.preventDefault();
            var $checkedRadio = this.$('input[type="radio"]:checked');
    
            // first we check that the user has selected a openpay as add payment method
            if ($checkedRadio.length === 1 && this.isNewPaymentRadio($checkedRadio) && $checkedRadio.data('provider') === 'openpay') {
                return this._createOpenpayURL(ev, $checkedRadio, true);
            } else {
                return this._super.apply(this, arguments);
            }
        },
    });
});
    