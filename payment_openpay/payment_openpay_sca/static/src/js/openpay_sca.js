odoo.define('payment_openpay.openpay', function (require) {
    "use strict";
    
    var ajax = require('web.ajax');
    var core = require('web.core');
    
    var qweb = core.qweb;
    var _t = core._t;
    
    ajax.loadXML('/payment_openpay/static/src/xml/openpay_templates.xml', qweb);
    
    if ($.blockUI)
    {
        // our message needs to appear above the modal dialog
        $.blockUI.defaults.baseZ = 2147483647; //same z-index as OpenpayCheckout
        $.blockUI.defaults.css.border = '0';
        $.blockUI.defaults.css["background-color"] = '';
        $.blockUI.defaults.overlayCSS["opacity"] = '0.9';
    }
    
    require('web.dom_ready');
    if (!$('.o_payment_form').length)
    {
        return Promise.reject("DOM doesn't contain '.o_payment_form'");
    }
    
    var observer = new MutationObserver(function (mutations, observer)
    {
        for (var i = 0; i < mutations.length; ++i) {
            for (var j = 0; j < mutations[i].addedNodes.length; ++j) {
                if (mutations[i].addedNodes[j].tagName.toLowerCase() === "form" && mutations[i].addedNodes[j].getAttribute('provider') === 'openpay') {
                    _redirectToOpenpayCheckout($(mutations[i].addedNodes[j]));
                }
            }
        }
    });
    
    function displayError(message)
    {
        var wizard = $(qweb.render('openpay.error', {'msg': message || _t('Payment error')}));
        wizard.appendTo($('body')).modal({'keyboard': true});
        if ($.blockUI) {
            $.unblockUI();
        }
        $("#o_payment_form_pay").removeAttr('disabled');
    }
    
    function _redirectToOpenpayCheckout(providerForm)
    {
        // Open Checkout with further options
        if ($.blockUI)
        {
            var msg = _t("Just one more second, we are redirecting you to Openpay...");
            $.blockUI({
                'message':  '<h2 class="text-white"><img src="/web/static/src/img/spin.png" class="fa-pulse"/>' +
                            '   <br />' + msg +
                            '</h2>'
            });
        }
    
        var paymentForm = $('.o_payment_form');
        if (!paymentForm.find('i').length)
        {
            paymentForm.append('<i class="fa fa-spinner fa-spin"/>');
            paymentForm.attr('disabled', 'disabled');
        }

        var url = $("#openpay_url").val();
        if (url) // Si hay URL
        {
            window.location.href = url;
        }
        else
        {
            window.location.reload();
        }
    }

    observer.observe(document.body, { childList: true });
    _redirectToOpenpayCheckout($('form[provider="openpay"]'));
});
    