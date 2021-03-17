# -*- coding: utf-8 -*-
# Copyright 2016 mulaWare - https://mulaware.com/
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json
import requests
import pprint

from datetime import date
from datetime import datetime
from datetime import timedelta

from odoo.tests.common import HttpCase
from odoo import api, exceptions, fields, models, tools, _
from odoo.tools.translate import _
from odoo.exceptions import UserError, ValidationError
from calendar import monthrange

HOST = '127.0.0.1'
#PORT = tools.config['xmlrpc_port']
PORT = '8069'

class Webhook(models.Model):
    _inherit = 'webhook'

    @api.multi
    def run_thinkific_so_order_created(self):
        self.ensure_one()


        request = self.env.request.jsonrequest
        resource =  request['resource']
        self.last_request = request
        if resource == 'order':
            payload = request['payload']
            #print('payload --->>>',payload)
            user = payload['user']
            #print('user ---->>>',user)
            coupon = payload['coupon']


            vals = {
                    'name': request['id'],
                    'resource': request['resource'],
                    'action' : request['action'],
                    'tenant_global_id': request['tenant_global_id'],
                    'tenant_id': request['tenant_id'],
                    'created_at': request['created_at'],
                    #'timestamp': int(request['timestamp']),
                    'order_affiliate_referral_code': str(payload['affiliate_referral_code']),
                    'order_amount_cents': int(payload['amount_cents']),
                    'order_amount_dollars': float(payload['amount_dollars']),
                    'order_billing_name': str(payload['billing_name']),
                    'order_coupon': str(coupon['code']),
                    'order_coupon_id': int(coupon['id']),
                    'order_created_at': payload['created_at'],
                    'rec': int(payload['id']),
                    'order_number': payload['order_number'],
                    'order_payment_type': payload['payment_type'],
                    'order_product_id': int(payload['product_id']),
                    'order_product_name': payload['product_name'],
                    'order_status': payload['status'],
                    'order_user_email': user['email'],
                    'order_user_first_name': user['first_name'],
                    'order_user_id': int(user['id']),
                    'order_user_last_name': user['last_name'],
                    'order_state': 'draft',
            }
            thinkific_id = self.env['thinkific.sale'].create(vals)

        return thinkific_id



class ThinkificSale(models.Model):
    _name = 'thinkific.sale'
    _description = "Thinkific Sale"
    _order = "id desc"


    def _get_partner_id(self, thinkific_id):
        """ Get partner_id for thinkific_id """
        partner_obj = self.env['res.partner'].search([('thinkific_id','=', thinkific_id.order_user_id)], limit=1)

        if partner_obj:
            return partner_obj.id
        else:
            partner_obj = self.env['res.partner'].search([('name','=', thinkific_id.order_billing_name)], limit=1)
            if partner_obj:
                partner_obj.email = thinkific_id.order_user_email
                partner_obj.thinkific_id =  thinkific_id.order_user_id
                return partner_obj.id
            else:
                vals = {
                        'name': thinkific_id.order_billing_name,
                        'email': thinkific_id.order_user_email,
                        'thinkific_id': thinkific_id.order_user_id,
                        'customer': True,
                        'lang': 'es_MX',
                        'ref': 'Thinkific',
                        'company_id': self.env.user.company_id.id,
                }
                partner_obj = self.env['res.partner'].create(vals)
                return partner_obj.id

    def _get_product_id(self, thinkific_id):
        """ Get product_id for thinkific_id """
        product_obj = self.env['product.product'].search([('thinkific_id','=', thinkific_id.order_product_id)], limit=1)

        if product_obj:
            return product_obj.id
        else:
            product_obj = self.env['product.product'].search([('name','=', thinkific_id.order_product_name)], limit=1)
            if product_obj:
                product_obj.thinkific_id =  thinkific_id.order_product_id
                return product_obj.id
            else:
                vals = {
                        'name': thinkific_id.order_product_name,
                        'thinkific_id': thinkific_id.order_product_id,
                        'type': 'service',
                        'default_code': 'THNK-'+ thinkific_id.order_product_name,
                        'company_id': self.env.user.company_id.id,
                        'sale_ok': True,
                        'purchase_ok': False,
                        'taxes_id': [(4, self.env['account.tax'].search([('name','=', 'IVA(16%) VENTAS')], limit=1).id)]
                }
                product_obj = self.env['product.product'].create(vals)
                return product_obj.id

    def thinkific_so_cron(self):
        records = self.search([('order_state','=','draft')])
        for rec in records:
            if rec.order_amount_dollars <= 0:
                rec.order_state = 'cancel'
                break
            else:
                partner_id = rec._get_partner_id(rec)
                if not partner_id:
                    raise exceptions.ValidationError(_("Partner not found"))

                product_id = rec._get_product_id(rec)
                if not product_id:
                    raise exceptions.ValidationError(_("Product not found"))

                vals = {
                        'partner_id': partner_id,
                        'company_id' : self.env.user.company_id.id,
                        'state' : 'draft',
                        'client_order_ref': 'THINK-' + rec.order_number,
                        'thinkific_id': rec.id,
                        'l10n_mx_edi_payment_method_id': self.env.ref('l10n_mx_edi.payment_method_tarjeta_de_credito').id,
                        'fiscal_position_id': self.env['res.partner'].search([('id','=',partner_id)]).property_account_position_id.id or self.env.ref('l10n_mx.account_fiscal_position_616_fr').id,
                }

                sale_id = self.env['sale.order'].create(vals)
                if not sale_id:
                    raise exceptions.ValidationError(_("Error creating Sale Order"))

                sale_id.onchange_partner_id()

                sale_line_vals = {
                                 'product_id' : product_id,
                                 'product_uom_qty': 1,
                                 'qty_delivered': 1,
                                 'name' : rec.order_product_name,
                                 'price_unit' : rec.order_amount_dollars / 1.16,
                                 'tax_id': [(4, self.env['account.tax'].search([('name','=', 'IVA(16%) VENTAS')], limit=1).id)],
                                 'rec' : sale_id.id,
                }
                sale_line_ids = self.env['sale.order.line'].create(sale_line_vals)

                sale_id.action_confirm()

                order_date = str
                sale_id.write({'confirmation_date': datetime.strptime(rec.order_created_at,"%Y-%m-%dT%H:%M:%S.%fZ"),})

                sale_id.action_order_send()
                rec.sale_id =  sale_id.id

                rec.order_state = 'sale'

                return sale_id.id




    name = fields.Char(string="id")
    resource = fields.Char(string="resource")
    action = fields.Char(string="action")
    tenant_id = fields.Char(string="tenant_id")
    tenant_global_id = fields.Char(string="tenant_global_id")
    created_at = fields.Char(string="created_at")
    timestamp = fields.Date(string="timestamp")
    order_affiliate_referral_code = fields.Char(string="order_affiliate_referral_code")
    order_amount_cents = fields.Integer(string="order_amount_cents")
    order_amount_dollars = fields.Float(string="order_amount_dollars")
    order_billing_name = fields.Char(string="order_billing_name")
    order_coupon = fields.Char(string="order_coupon")
    order_coupon_id = fields.Integer(string="order_coupon_id")
    order_created_at = fields.Char(string="order_created_at")
    order_id = fields.Char(string="order_id")
    order_number = fields.Char(string="order_number")
    order_payment_type = fields.Char(string="payment_type")
    order_product_id = fields.Integer(string="order_product_id")
    order_product_name = fields.Char(string="order_product_name")
    order_status = fields.Char(string="order_status")
    order_user_id = fields.Integer(string="order_user_id")
    order_user_email = fields.Char(string="order_user_email")
    order_user_first_name = fields.Char(string="order_user_first_name")
    order_user_last_name = fields.Char(string="order_user_last_name")
    order_state = fields.Selection([
        ('draft', 'Quotation'),
        ('sale', 'Sales Order'),
        ('cancel', 'Cancelled'),
        ], string='Status',
         readonly=True,
         copy=False,
         index=True,
         default='draft')

    sale_id = fields.Many2one(comodel_name='sale.order',
                              string='Sale Order',
                              help="Sale Order",
                              )

    partner_id = fields.Many2one(comodel_name='res.partner',
                              string='Partner',
                              help="Partner",
                              related='sale_id.partner_id',
                              )

    state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
        ], string='Status',
         readonly=True,
         related='sale_id.state',
         copy=False,
         index=True,
         track_visibility='onchange',
         track_sequence=3,
         default='draft')


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    confirmation_date = fields.Datetime(string='Confirmation Date', readonly=False, index=True, help="Date on which the sales order is confirmed.", oldname="date_confirm", copy=False)


    def thinkific_so_cron_reminder(self):
        records = self.search([('state','=','sale'),('invoice_status','!=','invoiced'),('thinkific_id','!=',False)])
        for rec in records:
            confirmation_date = rec.confirmation_date + timedelta(days=5)
            if confirmation_date <= datetime.today():
                rec.action_order_send_reminder()
                return True

    def last_day_of_month(self,date_value):
        return date_value.replace(day = monthrange(date_value.year, date_value.month)[1])

    def thinkific_so_cron_invoice_end(self):
        records = self.search([('state','=','sale'),('invoice_status','!=','invoiced'),('thinkific_id','!=',False)])
        for rec in records:
            today = datetime.today().date()
            end_of_month = self.last_day_of_month(today)
            if today >= end_of_month:
                if rec.invoice_status != 'no' or rec.is_contract: # not in('invoiced','no'):
                    if True:
                        invoice_return = None
                        if rec.invoice_status == 'invoiced':
                            invoice_return = rec.invoice_ids.filtered(lambda r: r.state != 'cancel')
                            if invoice_return and invoice_return[0].state != 'draft': # in['factura_correcta', 'factura_cancelada']:
                                raise exceptions.ValidationError(_(rec))
                        else:

                            rec.l10n_mx_edi_payment_method_id = self.env.ref('l10n_mx_edi.payment_method_tarjeta_de_credito').id
                            rec.fiscal_position_id = self.env.ref('l10n_mx.account_fiscal_position_616_fr').id
                            if not rec.partner_id.vat:
                                rec.partner_id.vat = 'XAXX010101000'
                            #if rec.is_contract:
                            sale_order_line_id = self.env['sale.order.line'].search([('order_id','=',rec.id),('contract_id','!=',False)],limit=1)
                            contract_id = sale_order_line_id.contract_id
                            print("contract_id,sale_order_line_id ----->>>", contract_id, sale_order_line_id)
                            if contract_id:
                                invoice_return = contract_id.recurring_create_invoice()
                                invoice_br =invoice_return
                                print("invoice_return ----->>>", invoice_return)
                            else:
                                invoice_return = rec.action_invoice_create()
                                print("invoice_return ----->>>", invoice_return)
                                invoice_obj = self.env['account.invoice'].sudo()
                                invoice_br = invoice_obj.browse(invoice_return[0])
                        vals = {'factura_cfdi':True, }
                        if not invoice_br.l10n_mx_edi_usage:
                            vals.update({'l10n_mx_edi_usage': 'G03'})

                        if not invoice_br.l10n_mx_edi_payment_method_id:
                            vals.update({'l10n_mx_edi_payment_method_id': self.env.ref('l10n_mx_edi.payment_method_tarjeta_de_credito').id})

                        if not invoice_br.fiscal_position_id:
                            vals.update({'fiscal_position_id': self.env.ref('l10n_mx.account_fiscal_position_616_fr').id})

                        invoice_br.write(vals)
                        if True:
                            if invoice_br.state == 'draft':
                                invoice_br.self_invoice = True
                                invoice_br.action_invoice_open()


                                journal_id = self.env['account.journal'].search([('code','=','STRIP')],limit=1)
                                ctx = {'active_model': 'account.invoice', 'active_ids': [invoice_br.id], 'default_invoice_ids': [(4, invoice_br.id, None)]}
                                payment_id = self.env['account.payment'].with_context(
                                    ctx).create({
                                        'payment_date': rec.confirmation_date,
                                        'payment_method_id': journal_id.inbound_payment_method_ids[0].id,
                                        'l10n_mx_edi_payment_method_id': self.env.ref('l10n_mx_edi.payment_method_tarjeta_de_credito').id,
                                        'journal_id': journal_id.id,
                                        'communication': invoice_br.number,
                                        'amount': invoice_br.amount_total,
                                        'currency_id': invoice_br.currency_id.id,
                                        'payment_difference_handling': 'reconcile',
                                        'payment_type': 'inbound',
                                        'partner_type': 'customer',
                                        'partner_id': invoice_br.partner_id.id,
                                    })
                                if invoice_br.l10n_mx_edi_pac_status == 'signed':
                                    payment_id.action_validate_invoice_payment()



                            #_logger.info('uuid %s partner %s nombre %s uso_cfdi %s estus_pac %s', invoice_br.l10n_mx_edi_cfdi_uuid, invoice_br.partner_id.name, invoice_br.name, invoice_br.l10n_mx_edi_usage, invoice_br.l10n_mx_edi_pac_status)
                        else:
                            raise exceptions.ValidationError(_("Error creating Invoice"))
                            return
                    else:
                        raise exceptions.ValidationError(_("Error creating Sale Order"))
                        return
                else:
                    raise exceptions.ValidationError(_("Error creating Invoice, Sale Order already invoice"))
                    return

                return True

    def thinkific_so_cron_invoice(self):
        records = self.search([('state','=','sale'),('invoice_status','!=','invoiced'),('thinkific_id','!=',False)])
        for rec in records:
            confirmation_date = rec.confirmation_date + timedelta(days=7)
            if confirmation_date <= datetime.today():
                #rec.action_order_invoice_think(rec)
                if rec.invoice_status != 'no' or rec.is_contract: # not in('invoiced','no'):
                    if True:
                        invoice_return = None
                        if rec.invoice_status == 'invoiced':
                            invoice_return = rec.invoice_ids.filtered(lambda r: r.state != 'cancel')
                            if invoice_return and invoice_return[0].state != 'draft': # in['factura_correcta', 'factura_cancelada']:
                                raise exceptions.ValidationError(_(rec))
                        else:

                            rec.l10n_mx_edi_payment_method_id = self.env.ref('l10n_mx_edi.payment_method_tarjeta_de_credito').id
                            rec.fiscal_position_id = self.env.ref('l10n_mx.account_fiscal_position_616_fr').id
                            if not rec.partner_id.vat:
                                rec.partner_id.vat = 'XAXX010101000'
                            #if rec.is_contract:
                            sale_order_line_id = self.env['sale.order.line'].search([('order_id','=',rec.id),('contract_id','!=',False)],limit=1)
                            contract_id = sale_order_line_id.contract_id
                            print("contract_id,sale_order_line_id ----->>>", contract_id, sale_order_line_id)
                            if contract_id:
                                invoice_return = contract_id.recurring_create_invoice()
                                invoice_br =invoice_return
                                print("invoice_return ----->>>", invoice_return)
                            else:
                                invoice_return = rec.action_invoice_create()
                                print("invoice_return ----->>>", invoice_return)
                                invoice_obj = self.env['account.invoice'].sudo()
                                invoice_br = invoice_obj.browse(invoice_return[0])
                        vals = {'factura_cfdi':True, }
                        if not invoice_br.l10n_mx_edi_usage:
                            vals.update({'l10n_mx_edi_usage': 'G03'})

                        if not invoice_br.l10n_mx_edi_payment_method_id:
                            vals.update({'l10n_mx_edi_payment_method_id': self.env.ref('l10n_mx_edi.payment_method_tarjeta_de_credito').id})

                        if not invoice_br.fiscal_position_id:
                            vals.update({'fiscal_position_id': self.env.ref('l10n_mx.account_fiscal_position_616_fr').id})

                        invoice_br.write(vals)
                        if True:
                            if invoice_br.state == 'draft':
                                invoice_br.self_invoice = True
                                invoice_br.action_invoice_open()


                                journal_id = self.env['account.journal'].search([('code','=','STRIP')],limit=1)
                                ctx = {'active_model': 'account.invoice', 'active_ids': [invoice_br.id], 'default_invoice_ids': [(4, invoice_br.id, None)]}
                                payment_id = self.env['account.payment'].with_context(
                                    ctx).create({
                                        'payment_date': rec.confirmation_date,
                                        'payment_method_id': journal_id.inbound_payment_method_ids[0].id,
                                        'l10n_mx_edi_payment_method_id': self.env.ref('l10n_mx_edi.payment_method_tarjeta_de_credito').id,
                                        'journal_id': journal_id.id,
                                        'communication': invoice_br.number,
                                        'amount': invoice_br.amount_total,
                                        'currency_id': invoice_br.currency_id.id,
                                        'payment_difference_handling': 'reconcile',
                                        'payment_type': 'inbound',
                                        'partner_type': 'customer',
                                        'partner_id': invoice_br.partner_id.id,
                                    })
                                if invoice_br.l10n_mx_edi_pac_status == 'signed':
                                    payment_id.action_validate_invoice_payment()



                            #_logger.info('uuid %s partner %s nombre %s uso_cfdi %s estus_pac %s', invoice_br.l10n_mx_edi_cfdi_uuid, invoice_br.partner_id.name, invoice_br.name, invoice_br.l10n_mx_edi_usage, invoice_br.l10n_mx_edi_pac_status)
                        else:
                            raise exceptions.ValidationError(_("Error creating Invoice"))
                            return
                    else:
                        raise exceptions.ValidationError(_("Error creating Sale Order"))
                        return
                else:
                    raise exceptions.ValidationError(_("Error creating Invoice, Sale Order already invoice"))
                    return

                return True

    @api.multi
    def action_order_invoice_think(self,rec):
        '''
        This function opens a new invoice for a given sale order
        '''
        self.ensure_one()

        if rec.invoice_status != 'no' or rec.is_contract: # not in('invoiced','no'):
            if True:
                invoice_return = None
                if rec.invoice_status == 'invoiced':
                    invoice_return = rec.invoice_ids.filtered(lambda r: r.state != 'cancel')
                    if invoice_return and invoice_return[0].state != 'draft': # in['factura_correcta', 'factura_cancelada']:
                        raise exceptions.ValidationError(_(rec))
                else:
                    if not rec.l10n_mx_edi_payment_method_id:
                        rec.l10n_mx_edi_payment_method_id = self.env.ref('l10n_mx_edi.payment_method_tarjeta_de_credito').id
                    if not rec.partner_id.vat:
                        rec.partner_id.vat = 'XAXX010101000'
                    if rec.is_contract:
                        sale_order_line_id = self.env['sale.order.line'].search([('rec','=',rec.id),('contract_id','!=',False)],limit=1)
                        contract_id = sale_order_line_id.contract_id
                        print("contract_id,sale_order_line_id ----->>>", contract_id, sale_order_line_id)
                        if contract_id:
                            invoice_return = contract_id.recurring_create_invoice()
                            invoice_br =invoice_return
                            print("invoice_return ----->>>", invoice_return)
                    else:
                        invoice_return = order_br.action_invoice_create()
                        print("invoice_return ----->>>", invoice_return)
                        invoice_obj = self.env['account.invoice'].sudo()
                        invoice_br = invoice_obj.browse(invoice_return[0])
                vals = {'factura_cfdi':True, }
                if not invoice_br.l10n_mx_edi_usage:
                    vals.update({'l10n_mx_edi_usage': 'G03'})

                if not invoice_br.l10n_mx_edi_payment_method_id:
                    vals.update({'l10n_mx_edi_payment_method_id': self.env.ref('l10n_mx_edi.payment_method_tarjeta_de_credito').id})

                invoice_br.write(vals)
                if True:
                    if invoice_br.state == 'draft':
                        invoice_br.self_invoice = True
                        invoice_br.action_invoice_open()

                    _logger.info('uuid %s partner %s nombre %s uso_cfdi %s estus_pac %s', invoice_br.l10n_mx_edi_cfdi_uuid, invoice_br.partner_id.name, invoice_br.name, invoice_br.l10n_mx_edi_usage, invoice_br.l10n_mx_edi_pac_status)
                else:
                    raise exceptions.ValidationError(_("Error creating Invoice"))
                    return
            else:
                raise exceptions.ValidationError(_("Error creating Sale Order"))
                return
        else:
            raise exceptions.ValidationError(_("Error creating Invoice, Sale Order already invoice"))
            return

        return


    @api.multi
    def action_order_send(self):
        '''
        This function opens a window to compose an email, with the edi sale template message loaded by default
        '''
        self.ensure_one()

        template_id = self.env.ref('thinkific.thinkific_so_email').id

        template = self.env['mail.template'].browse(template_id)

        lang = self.env.context.get('lang')

        ctx = self.env.context.copy()
        ctx.update({
            'default_model': 'sale.order',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'model_description': self.with_context(lang=lang).type_name,
            'custom_layout': "mail.mail_notification_paynow",
            'proforma': self.env.context.get('proforma', False),
            'force_email': True
        })

        send_mail = template.with_context(ctx).send_mail(self.id, force_send=True)
        #print("ctx ----->>", send_mail, ctx)
        return

    @api.multi
    def action_order_send_reminder(self):
        '''
        This function opens a window to compose an email, with the edi sale template message loaded by default
        '''
        self.ensure_one()

        template_id = self.env.ref('thinkific.thinkific_so_email_reminder').id

        template = self.env['mail.template'].browse(template_id)

        lang = self.env.context.get('lang')

        ctx = self.env.context.copy()
        ctx.update({
            'default_model': 'sale.order',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'model_description': self.with_context(lang=lang).type_name,
            'custom_layout': "mail.mail_notification_paynow",
            'proforma': self.env.context.get('proforma', False),
            'force_email': True
        })

        send_mail = template.with_context(ctx).send_mail(self.id, force_send=True)
        #print("ctx ----->>", send_mail, ctx)
        return

    thinkific_id = fields.Many2one(comodel_name='thinkific.sale',
                              string='Thinkific Order',
                              help="Thinkific Sale Order",
                              )

class Partner(models.Model):
    _inherit = 'res.partner'

    thinkific_id = fields.Integer(string="Thinkific id")

class ProductProduct(models.Model):
    _inherit = 'product.product'

    thinkific_id = fields.Integer(string="Thinkific id")
