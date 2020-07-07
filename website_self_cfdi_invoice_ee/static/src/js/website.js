odoo.define('website_self_cfdi_invoice_ee', function(require) {
    'use strict';

    var base = require('web_editor.base');
    var core    = require('web.core');
    var Tour    = require('web.Tour');
    var Model   = require('web.Model');
    var Session = require('web.Session');

    base.ready().done(function () {
        Tour.register({
            id:   'website_invoice_mx_tour',
            name: "Test the contact us form",
            path: '/portal/facturacliente',
            mode: 'test',
            steps: [
                {
                    title:          "RFC Cliente",
                    element:        "input[name=rfc_partner]",
                    sampleText:     "PODG890615269",
                },
                {
                    title:          "Folio Pedido de Venta",
                    element:        "input[name=order_number]",
                    sampleText:     "SALE001",
                },
                {
                    title:          "Send the form",
                    element:        ".o_website_form_send"
                },
                {
                    title:          "Check we were redirected to the success page",
                    waitFor:        "#wrap:has(h1:contains('Thanks')):has(div.alert-success)"
                }
            ]
        });
    });

    return {};
});
