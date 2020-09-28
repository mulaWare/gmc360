import openpay

import logging
import requests
import pprint
from werkzeug import urls
from requests.exceptions import HTTPError

from odoo import api, models, fields, _
from odoo.exceptions import ValidationError
from odoo.addons.payment_openpay_sca.controllers.main import OpenpayControllerSCA as OpenpayController
from odoo.addons.payment_openpay.models.payment import INT_CURRENCIES
from odoo.tools.float_utils import float_round

try:
    # base64.encodestring is deprecated in Python 3.x
    from base64 import encodebytes
except ImportError:
    # Python 2.x
    from base64 import encodestring as encodebytes

_logger = logging.getLogger(__name__)


class PaymentAcquirerOpenpaySCA(models.Model):
    _inherit = "payment.acquirer"

    def openpay_form_generate_values(self, tx_values):
        self.ensure_one()

        base_url = self.get_base_url()
        openpay_session_data = {
            "url_success": urls.url_join(base_url, OpenpayController._success_url) + "?reference=%s" % tx_values["reference"],
            "url_cancel": urls.url_join(base_url, OpenpayController._cancel_url) + "?reference=%s" % tx_values["reference"],

            "customer_first_name": tx_values.get("partner_first_name"),
            "customer_last_name": tx_values.get("partner_last_name"),
            "customer_email": tx_values.get("partner_email") or tx_values.get("billing_partner_email"),

            "tx_reference": tx_values["reference"],
            "tx_amount": float_round(tx_values["amount"], 2),
            "tx_currency": tx_values["currency"].name
        }
        tx_values["openpay_url"] = self._generar_url_openpay(openpay_session_data)

        return tx_values



    def _generar_url_openpay(self, kwargs):
        self.ensure_one()

        acquirer = self.sudo()
        openpay_secret_key = acquirer.openpay_secret_key
        openpay_id = acquirer.openpay_id
        openpay_sandbox = acquirer.openpay_sandbox
        openpay_transferencia = acquirer.openpay_transferencia

        openpay.api_key = openpay_secret_key
        openpay.verify_ssl_certs = False
        openpay.merchant_id = openpay_id
        openpay.production = not openpay_sandbox

        folio = kwargs.get("tx_reference")

        metodo = "card"

        if openpay_transferencia:
            metodo = "bank_account"

        customer = openpay.Customer.create(
            name = kwargs.get("customer_first_name"),
            last_name = kwargs.get("customer_last_name"),
            email= kwargs.get("customer_email"),
            phone_number="5584218491")

        charge = customer.charges.create(
            method = metodo,
            amount = kwargs.get("tx_amount"),
            description = folio,
            use_3d_secure = True,
            send_email = False,
            confirm = False,
            redirect_url = kwargs.get("url_success"))

        transaction = (
        self.env["payment.transaction"]
        .sudo()
        .search([("reference", "=", folio)])
        )

        transaction.openpay_charge_id = charge.id
        transaction.openpay_customer_id = customer.id

        url = ""
        if openpay_transferencia :
            dashbord_path = "https://sandbox-dashboard.openpay.mx" if openpay_sandbox else "https://dashboard.openpay.mx"

            url = dashbord_path + "/spei-pdf/" + openpay_id + "/" + charge.id
        else :
            payment_method = charge.payment_method
            url = payment_method.url

        return url




    def _obtener_cargo(self, customer_id, charge_id, data=False, method="POST"):
        self.ensure_one()

        acquirer = self.sudo()
        openpay_secret_key = acquirer.openpay_secret_key
        openpay_id = acquirer.openpay_id
        openpay_sandbox = acquirer.openpay_sandbox

        openpay.api_key = openpay_secret_key
        openpay.verify_ssl_certs = False
        openpay.merchant_id = openpay_id
        openpay.production = not openpay_sandbox

        base_url = openpay.get_api_base()
        request_url = base_url + "/v1/" + openpay_id + "/customers/" + customer_id + "/charges/" + charge_id

        user_string = '%s:%s' % (openpay_secret_key, '')
        base64string = encodebytes(bytes(user_string, encoding='utf-8'))
        base64string = base64string.decode('utf-8').replace('\n', '')

        headers = {
            "AUTHORIZATION": "Basic %s" % base64string
        }

        response = requests.request("GET", request_url, headers=headers)

        # Openpay can send 4XX errors for payment failure (not badly-formed requests)
        # check if error `code` is present in 4XX response and raise only if not
        # cfr https://openpay.com/docs/error-codes
        # these can be made customer-facing, as they usually indicate a problem with the payment
        # (e.g. insufficient funds, expired card, etc.)
        # if the context key `openpay_manual_payment` is set then these errors will be raised as ValidationError,
        # otherwise, they will be silenced, and the will be returned no matter the status.
        # This key should typically be set for payments in the present and unset for automated payments
        # (e.g. through crons)
        if not response.ok and self._context.get('openpay_manual_payment') and (400 <= response.status_code < 500 and response.json().get('error', {}).get('code')):
            try:
                response.raise_for_status()
            except HTTPError:
                _logger.error(resp.text)
                openpay_error = response.json().get('error', {}).get('message', '')
                error_msg = " " + (_("Openpay gave us the following info about the problem: '%s'") % openpay_error)
                raise ValidationError(error_msg)
        return response.json()









    def _openpay_request(self, url, data=False, method="POST"):
        self.ensure_one()
        openpay_url = 'https://%s/' % (self._get_openpay_api_url())
        url = urls.url_join(openpay_url, url)
        headers = {
            "AUTHORIZATION": "Bearer %s" % self.sudo().openpay_secret_key,
            "Openpay-Version": "2019-05-16",  # SetupIntent need a specific version
        }
        resp = requests.request(method, url, data=data, headers=headers)
        # Openpay can send 4XX errors for payment failure (not badly-formed requests)
        # check if error `code` is present in 4XX response and raise only if not
        # cfr https://openpay.com/docs/error-codes
        # these can be made customer-facing, as they usually indicate a problem with the payment
        # (e.g. insufficient funds, expired card, etc.)
        # if the context key `openpay_manual_payment` is set then these errors will be raised as ValidationError,
        # otherwise, they will be silenced, and the will be returned no matter the status.
        # This key should typically be set for payments in the present and unset for automated payments
        # (e.g. through crons)
        if not resp.ok and self._context.get('openpay_manual_payment') and (400 <= resp.status_code < 500 and resp.json().get('error', {}).get('code')):
            try:
                resp.raise_for_status()
            except HTTPError:
                _logger.error(resp.text)
                openpay_error = resp.json().get('error', {}).get('message', '')
                error_msg = " " + (_("Openpay gave us the following info about the problem: '%s'") % openpay_error)
                raise ValidationError(error_msg)
        return resp.json()



    def _create_setup_intent(self, kwargs):
        self.ensure_one()
        params = {"usage": "off_session"}
        _logger.info(
            "_openpay_create_setup_intent: Sending values to openpay, values:\n%s",
            pprint.pformat(params),
        )

        res = self._openpay_request("setup_intents", params)

        _logger.info(
            "_openpay_create_setup_intent: Values received:\n%s", pprint.pformat(res)
        )
        return res

    @api.model
    def openpay_s2s_form_process(self, data):
        card_number = ""

        payment_method = data.get("payment_method", {})
        if payment_method.get("type") == "card" :
            card_number = data.get("card", {}).get("card_number")
        else :
            card_number = "TRANSFER"

        payment_token = (
            self.env["payment.token"]
            .sudo()
            .create(
                {
                    "acquirer_id": int(data["acquirer_id"]),
                    "partner_id": int(data["partner_id"]),
                    "openpay_payment_method": data.get("payment_method"),
                    "name": card_number,
                    "acquirer_ref": data.get("customer"),
                }
            )
        )
        return payment_token

    def openpay_s2s_form_validate(self, data):
        return True











class PaymentTransactionOpenpaySCA(models.Model):
    _inherit = "payment.transaction"

    openpay_charge_id = fields.Char(
        string="Openpay Charge ID", readonly=True
    )
    openpay_customer_id = fields.Char(string='Openpay Customer ID', readonly=True)

    def form_feedback(self, data, acquirer_name):
        if data.get("reference") and acquirer_name == "openpay":
            transaction = self.env["payment.transaction"].search(
                [("reference", "=", data["reference"])]
            )

            response = transaction.acquirer_id._obtener_cargo(transaction.openpay_customer_id, transaction.openpay_charge_id)

            data.update(response)
            _logger.info(
                "Openpay: entering form_feedback with post data %s"
                % pprint.pformat(data)
            )
        # note: luckily, the base openpay module did not override this method, avoiding
        # me from using a context key to avoid this call in the parent model
        return super(PaymentTransactionOpenpaySCA, self).form_feedback(data, acquirer_name)



    def _openpay_form_get_invalid_parameters(self, data):

        invalid_parameters = []

        amount_recibido = data.get("amount")
        amount_transaccion = float_round(self.amount, 2)
        if amount_recibido != amount_transaccion:
            invalid_parameters.append(("Amount", amount_recibido, amount_transaccion))

        """ COMENTADO PARA PRUEBAS
        currency_recibido = data.get("currency").upper()
        currency_transaccion = self.currency_id.name
        if currency_recibido != currency_transaccion:
            invalid_parameters.append(
                ("Currency",currency_recibido, currency_transaccion)
            )
        """

        if (
            data.get("payment_intent")
            and data.get("payment_intent") != self.openpay_charge_id
        ):
            invalid_parameters.append(
                (
                    "Payment Intent",
                    data.get("payment_intent"),
                    self.openpay_charge_id,
                )
            )

        return invalid_parameters








    def _get_json_fields(self):
        res = super()._get_json_fields()
        res.append('openpay_customer_id')
        return res

    def _get_processing_info(self):
        res = super()._get_processing_info()
        if self.acquirer_id.provider == 'openpay':
            openpay_info = {
                'openpay_charge_id': self.openpay_charge_id,
                'openpay_customer_id': self.openpay_customer_id,
                'openpay_publishable_key': self.acquirer_id.openpay_publishable_key,
            }
            res.update(openpay_info)
        return res

    def _create_openpay_charge(self, acquirer_ref=None, tokenid=None, email=None):
        raise NotImplementedError(
            "This method can no longer be used with the payment_openpay_sca module."
        )



    def _openpay_create_payment_intent(self, acquirer_ref=None, email=None):
        if self.openpay_charge_id:
            _logger.info(
                "_openpay_create_payment_intent: trying to create an intent when one already exists (tx #%s), refetching values for intent %s",
                self.id, self.openpay_charge_id
            )
            res =  self.acquirer_id._openpay_request("payment_intents/%s" % self.openpay_charge_id, method="GET")
            _logger.info(
                "_openpay_create_payment_intent: Values received:\n%s", pprint.pformat(res)
                )
            return res
        if not self.payment_token_id.openpay_payment_method:
            # old token before installing openpay_sca, need to fetch data from the api
            self.payment_token_id._openpay_sca_migrate_customer()
        charge_params = {
            "amount": int(
                self.amount
                if self.currency_id.name in INT_CURRENCIES
                else float_round(self.amount * 100, 2)
            ),
            "currency": self.currency_id.name.lower(),
            "confirm": True,
            "off_session": True,
            "payment_method": self.payment_token_id.openpay_payment_method,
            "customer": self.payment_token_id.acquirer_ref,
            "description": self.reference,
        }
        if not self.env.context.get('off_session'):
            charge_params.update(setup_future_usage='off_session', off_session=False)
        _logger.info(
            "_openpay_create_payment_intent: Sending values to openpay, values:\n%s",
            pprint.pformat(charge_params),
        )

        res = self.acquirer_id._openpay_request("payment_intents", charge_params)
        if res.get("charges") and res.get("charges").get("total_count"):
            res = res.get("charges").get("data")[0]

        _logger.info(
            "_openpay_create_payment_intent: Values received:\n%s", pprint.pformat(res)
        )
        return res

    def openpay_s2s_do_transaction(self, **kwargs):
        self.ensure_one()
        result = self._openpay_create_payment_intent(
            acquirer_ref=self.payment_token_id.acquirer_ref, email=self.partner_email
        )
        return self._openpay_s2s_validate_tree(result)

    def _create_openpay_refund(self):
        refund_params = {
            "charge": self.acquirer_reference,
            "amount": int(
                float_round(self.amount * 100, 2)
            ),  # by default, openpay refund the full amount (we don't really need to specify the value)
            "metadata[reference]": self.reference,
        }

        _logger.info(
            "_create_openpay_refund: Sending values to openpay URL, values:\n%s",
            pprint.pformat(refund_params),
        )
        res = self.acquirer_id._openpay_request("refunds", refund_params)
        _logger.info("_create_openpay_refund: Values received:\n%s", pprint.pformat(res))
        return res

    @api.model
    def _openpay_form_get_tx_from_data(self, data):
        """ Given a data dict coming from openpay, verify it and find the related
        transaction record. """
        reference = data.get("reference")
        if not reference:
            openpay_error = data.get("error", {}).get("message", "")
            _logger.error(
                "Openpay: invalid reply received from openpay API, looks like "
                "the transaction failed. (error: %s)",
                openpay_error or "n/a",
            )
            error_msg = _("We're sorry to report that the transaction has failed.")
            if openpay_error:
                error_msg += " " + (
                    _("Openpay gave us the following info about the problem: '%s'")
                    % openpay_error
                )
            error_msg += " " + _(
                "Perhaps the problem can be solved by double-checking your "
                "credit card details, or contacting your bank?"
            )
            raise ValidationError(error_msg)

        tx = self.search([("reference", "=", reference)])
        if not tx:
            error_msg = _("Openpay: no order found for reference %s") % reference
            _logger.error(error_msg)
            raise ValidationError(error_msg)
        elif len(tx) > 1:
            error_msg = _("Openpay: %s orders found for reference %s") % (
                len(tx),
                reference,
            )
            _logger.error(error_msg)
            raise ValidationError(error_msg)
        return tx[0]

    def _openpay_s2s_validate_tree(self, tree):
        self.ensure_one()
        if self.state not in ("draft", "pending"):
            _logger.info(
                "Openpay: trying to validate an already validated tx (ref %s)",
                self.reference,
            )
            return True

        status = tree.get("status")
        tx_id = tree.get("id")
        tx_customer_id = tree.get("customer_id")
        vals = {"date": fields.datetime.now(), "acquirer_reference": tx_id, "openpay_charge_id": tx_id, "openpay_customer_id": tx_customer_id}

        if status == "completed":
            tx_fee = tree.get("fee").get("amount")
            vals.setdefault("fee", tx_fee)

            self.write(vals)
            self._set_transaction_done()
            self.execute_callback()
            if self.type == "form_save" or True: #---------- CORREGIR --------------
                s2s_data = {
                    "customer": tree.get("customer"),
                    "payment_method": tree.get("payment_method"),
                    "card": tree.get("card"),
                    "acquirer_id": self.acquirer_id.id,
                    "partner_id": self.partner_id.id,
                }
                token = self.acquirer_id.openpay_s2s_form_process(s2s_data)
                self.payment_token_id = token.id
            if self.payment_token_id:
                self.payment_token_id.verified = True
            return True
        if status in ("in_progress", "charge_pending"):
            self.write(vals)
            self._set_transaction_pending()
            return True
        else:
            error = tree.get("failure_message") or tree.get('error', {}).get('message')
            self._set_transaction_error(error)
            return False




class PaymentTokenOpenpaySCA(models.Model):
    _inherit = "payment.token"

    openpay_payment_method = fields.Char("Payment Method ID")

    @api.model
    def openpay_create(self, values):
        if values.get("openpay_payment_method") and not values.get("acquirer_ref"):
            partner_id = self.env["res.partner"].browse(values.get("partner_id"))
            payment_acquirer = self.env["payment.acquirer"].browse(
                values.get("acquirer_id")
            )

            # link customer with payment method
            api_url_payment_method = (
                "payment_methods/%s/attach" % values["openpay_payment_method"]
            )

            # ---------- CORREGIR --------------
            return {"acquirer_ref": "xxxxxx"}
        return values

    def _openpay_create_customer(self, token, description=None, acquirer_id=None):
        raise NotImplementedError(
            "This method can no longer be used with the payment_openpay_sca module."
        )

    def _openpay_sca_migrate_customer(self):
        """Migrate a token from the old implementation of Openpay to the SCA one.

        In the old implementation, it was possible to create a valid charge just by
        giving the customer ref to ask Openpay to use the default source (= default
        card). Since we have a one-to-one matching between a saved card, this used to
        work well - but now we need to specify the payment method for each call and so
        we have to contact openpay to get the default source for the customer and save it
        in the payment token.
        This conversion will happen once per token, the first time it gets used following
        the installation of the module."""
        self.ensure_one()
        url = "customers/%s" % (self.acquirer_ref)
        data = self.acquirer_id._openpay_request(url, method="GET")
        sources = data.get('sources', {}).get('data', [])
        pm_ref = False
        if sources:
            if len(sources) > 1:
                _logger.warning('openpay sca customer conversion: there should be a single saved source per customer!')
            pm_ref = sources[0].get('id')
        else:
            url = 'payment_methods'
            params = {
                'type': 'card',
                'customer': self.acquirer_ref,
            }
            payment_methods = self.acquirer_id._openpay_request(url, params, method='GET')
            cards = payment_methods.get('data', [])
            if len(cards) > 1:
                _logger.warning('openpay sca customer conversion: there should be a single saved source per customer!')
            pm_ref = cards and cards[0].get('id')
        if not pm_ref:
            raise ValidationError(_('Unable to convert Openpay customer for SCA compatibility. Is there at least one card for this customer in the Openpay backend?'))
        self.openpay_payment_method = pm_ref
        _logger.info('converted old customer ref to sca-compatible record for payment token %s', self.id)
