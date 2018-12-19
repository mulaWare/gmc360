# -*- coding: utf-8 -*-

import base64
from itertools import groupby
import re
import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta
from io import BytesIO
import requests
from pytz import timezone

from lxml import etree
from lxml.objectify import fromstring
from suds.client import Client

from odoo import _, api, fields, models, tools
from odoo.tools.xml_utils import _check_with_xsd
from odoo.tools import DEFAULT_SERVER_TIME_FORMAT
from odoo.tools import float_round
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_repr

CFDI_TEMPLATE = 'l10n_mx_edi.cfdiv32'
CFDI_TEMPLATE_33 = 'l10n_mx_edi.cfdiv33'
CFDI_XSLT_CADENA = 'l10n_mx_edi/data/%s/cadenaoriginal.xslt'
CFDI_XSLT_CADENA_TFD = 'l10n_mx_edi/data/xslt/3.3/cadenaoriginal_TFD_1_1.xslt'
# Mapped from original SAT state to l10n_mx_edi_sat_status selection value
# https://consultaqr.facturaelectronica.sat.gob.mx/ConsultaCFDIService.svc?wsdl
CFDI_SAT_QR_STATE = {
    'No Encontrado': 'not_found',
    'Cancelado': 'cancelled',
    'Vigente': 'valid',
}

_logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class AccountInvoice(models.Model):
    _name = 'account.invoice'
    _inherit = 'account.invoice'


    @api.multi
    def _l10n_mx_edi_create_cfdi_values(self):
        '''Create the values to fill the CFDI template.
        '''
        self.ensure_one()
        precision_digits = self.env['decimal.precision'].precision_get('Account')
        partner_id = self.partner_id
        if self.partner_id.type != 'invoice':
            partner_id = self.partner_id.commercial_partner_id
            self.message_post(body=_(
                'The business partner address was used for the generation of '
                'the CFDI, since the customer address is not a billing address.'),
                subtype='account.mt_invoice_validated')
        values = {
            'record': self,
            'currency_name': self.currency_id.name,
            'supplier': self.company_id.partner_id.commercial_partner_id,
            'issued': self.journal_id.l10n_mx_address_issued_id,
            'customer': partner_id,
            'fiscal_position': self.company_id.partner_id.property_account_position_id,
            'payment_method': self.l10n_mx_edi_payment_method_id.code,
            'use_cfdi': self.l10n_mx_edi_usage,
            'conditions': self._get_string_cfdi(
                self.payment_term_id.name, 1000) if self.payment_term_id else False,
        }

        values.update(self._l10n_mx_get_serie_and_folio(self.number))
        ctx = dict(company_id=self.company_id.id, date=self.date_invoice)
        mxn = self.env.ref('base.MXN').with_context(ctx)
        invoice_currency = self.currency_id.with_context(ctx)
        values['rate'] = ('%.6f' % (
            invoice_currency.compute(1, mxn, round=False))) if self.currency_id.name != 'MXN' else False

        version = self.l10n_mx_edi_get_pac_version()
        values['document_type'] = 'ingreso' if self.type == 'out_invoice' else 'egreso'

        term_ids = self.payment_term_id.line_ids

        if version == '3.2':
            if len(term_ids.ids) > 1:
                values['payment_policy'] = 'Pago en parcialidades'
            else:
                values['payment_policy'] = 'Pago en una sola exhibición'
        elif version == '3.3':
            # In CFDI 3.3 - SAT 2018 rule 2.7.1.44, the payment policy is PUE
            # if the invoice will be paid before 17th of the following month,
            # PPD otherwise
            date_pue = (fields.Date.from_string(self.date_invoice) +
                        relativedelta(day=17, months=1))
            date_due = fields.Date.from_string(self.date_due)

            values['payment_policy'] = 'PPD' if (
                self.payment_term_id.name != 'PUE') else 'PUE'

        domicile = self.journal_id.l10n_mx_address_issued_id or self.company_id
        values['domicile'] = '%s %s, %s' % (
                domicile.city,
                domicile.state_id.name,
                domicile.country_id.name,
        )

        values['decimal_precision'] = precision_digits
        subtotal_wo_discount = lambda l: float_round(
            l.price_subtotal / (1 - l.discount/100) if l.discount != 100 else
            l.price_unit * l.quantity, int(precision_digits))
        values['subtotal_wo_discount'] = subtotal_wo_discount
        get_discount = lambda l, d: ('%.*f' % (
            int(d), subtotal_wo_discount(l) - l.price_subtotal)) if l.discount else False
        values['total_discount'] = get_discount
        total_discount = sum([float(get_discount(p, precision_digits)) for p in self.invoice_line_ids])
        values['amount_untaxed'] = '%.*f' % (
            precision_digits, sum([subtotal_wo_discount(p) for p in self.invoice_line_ids]))
        values['amount_discount'] = '%.*f' % (precision_digits, total_discount) if total_discount else None

        values['taxes'] = self._l10n_mx_edi_create_taxes_cfdi_values()
        values['amount_total'] = '%0.*f' % (precision_digits,
            float(values['amount_untaxed']) - float(values['amount_discount'] or 0) + (
                values['taxes']['total_transferred'] or 0) - (values['taxes']['total_withhold'] or 0))

        values['tax_name'] = lambda t: {'ISR': '001', 'IVA': '002', 'IEPS': '003'}.get(
            t, False)

        if self.l10n_mx_edi_partner_bank_id:
            digits = [s for s in self.l10n_mx_edi_partner_bank_id.acc_number if s.isdigit()]
            acc_4number = ''.join(digits)[-4:]
            values['account_4num'] = acc_4number if len(acc_4number) == 4 else None
        else:
            values['account_4num'] = None

        return values
