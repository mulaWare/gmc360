# -*- coding: utf-8 -*-
from odoo.http import request
from odoo import http
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.portal.controllers.portal import CustomerPortal

class WebsiteSaleExtend(WebsiteSale):
    
    def _get_mandatory_billing_fields(self):
        field_list = super(WebsiteSaleExtend, self)._get_mandatory_billing_fields()
        field_list.append('zip')
        return field_list
    
    def _get_mandatory_shipping_fields(self):
        field_list = super(WebsiteSaleExtend, self)._get_mandatory_shipping_fields()
        field_list.append('zip')
        return field_list
    def values_postprocess(self, order, mode, values, errors, error_msg):
        res = super(WebsiteSaleExtend, self).values_postprocess(order, mode, values, errors, error_msg)
        if values.get('uso_cfdi'):
            order.write({'uso_cfdi':values.get('uso_cfdi')})
            res[0].update({'uso_cfdi':values.get('uso_cfdi')})
        return res

import sys
#reload(sys)  
#sys.setdefaultencoding('utf8')


class FacturaCliente(http.Controller):
    @http.route('/portal/facturacliente/', auth='public', website=True)
    def index(self, **kw):
        return http.request.render('website_self_cfdi_invoice_ee.index',
            {
                'fields': ['RFC','Folio',],
            })
    @http.route('/portal/facturacliente/results/',type="http", auth="public", csrf=False, website=True)
    def my_fact_portal_insert(self, **kwargs):
        ### Esta linea implementa los Captcha en el Portal ####
        # if kwargs.has_key('g-recaptcha-response') and request.website.is_captcha_valid(kwargs['g-recaptcha-response']):
        partner = request.env.user.partner_id
        rfc_partner = kwargs['rfc_partner'] or (partner.rfc and partner.rfc.replace('MX', '')) or False
        order_number = kwargs['order_number'] or False
        mail_to = kwargs.get('ticket_pos', False)
        ticket_pos = kwargs.get('mail_to', False)
        monto_total = kwargs.get('monto_total',0)
        
        partner_name = kwargs.get('partner_name', False)
        correo_electronico = kwargs.get('correo_electronico', False)
        uso_del_cfdi = kwargs.get('uso_del_cfdi', False)
        if 'ticket_pos' in kwargs:
            ticket_pos = kwargs['ticket_pos'] or True
        else:
            ticket_pos = False
        auto_invoice_obj = http.request.env['website.self.invoice.web']
        partner_obj = http.request.env['res.partner']
        partner_obj = partner_obj.sudo()
        partner_exist = partner_obj.search([('vat', '=', rfc_partner)], limit=1)
        partner_vals = {}
        if partner_name:
            partner_vals.update({'name' : partner_name})
        if correo_electronico:
            partner_vals.update({'email' : correo_electronico})
        if uso_del_cfdi:
            partner_vals.update({'uso_cfdi' : uso_del_cfdi})
        if partner_vals:
            if partner_exist:
                partner_exist.write(partner_vals)
            else:
                partner_vals.update({"vat" : rfc_partner})
                partner_exist = partner_obj.create(partner_vals)
                
        #### Si tenemos datos de una consulta previa los retornamos
        request_preview = auto_invoice_obj.search([('rfc_partner','=',rfc_partner),('order_number','=',order_number),('state','=','done')])
        if request_preview:
            attachment_obj = http.request.env['website.self.invoice.web.attach']
            attachments = attachment_obj.search([('website_auto_id','=',request_preview[0].id)])
            return http.request.render('website_self_cfdi_invoice_ee.html_result_thnks', 
                                                                                {
                                                                                'attachments': attachments,
                                                                                    })
        if not rfc_partner or not order_number: # or not mail_to:
            return http.request.render('website_self_cfdi_invoice_ee.html_result_error_inv', {'errores':['Los campos marcados con un ( * ) son Obligatorios.']})
        auto_invoice_id = auto_invoice_obj.create({
                                                    'rfc_partner': rfc_partner,
                                                    'order_number': order_number,
                                                    'monto_total' : monto_total,
                                                    'l10n_mx_edi_usage':uso_del_cfdi,
                                                    'ticket_pos': ticket_pos,
                                                    'partner_id': partner_exist.id,
                                                    })
        attachment_obj = http.request.env['website.self.invoice.web.attach']
        attachments = attachment_obj.search([('website_auto_id','=',auto_invoice_id.id)])
        if auto_invoice_id.error_message:
            return http.request.render('website_self_cfdi_invoice_ee.html_result_error_inv', {'errores':[auto_invoice_id.error_message]})
        return http.request.render('website_self_cfdi_invoice_ee.html_result_thnks', 
                                                                            {
                                                                            'attachments': attachments,
                                                                            })

    @http.route('/portal/consulta_factura/',type="http", auth="user", csrf=False, website=True)
    def request_invoice(self, **kwargs):
        if not kwargs:
            return http.request.render('website_self_cfdi_invoice_ee.index',
                                                                        {
                                                                            'fields': ['RFC','Folio',],
                                                                        })
        partner = request.env.user.partner_id
        rfc_partner = kwargs['rfc_partner'] or (partner.rfc and partner.rfc.replace('MX', '')) or False
        order_number = kwargs['order_number'] or False
        monto_total = kwargs.get('monto_total',0)

        auto_invoice_obj = http.request.env['website.self.invoice.web']
        try:
            auto_invoice = auto_invoice_obj.search([('order_number','=',order_number),
                ('rfc_partner','=',rfc_partner)])
            if auto_invoice:
                attachment_obj = http.request.env['website.self.invoice.web.attach']
                attachments = attachment_obj.search([('website_auto_id','=',auto_invoice[0].id)])
                return http.request.render('website_self_cfdi_invoice_ee.html_result_thnks', 
                                                                                    {
                                                                                    'attachments': attachments,
                                                                                    })
            else:
                error_message = "Su solicitud no pudo ser procesada.\nNo existe informacion para el Pedido %s." % order_number
                return http.request.render('website_self_cfdi_invoice_ee.html_result_error_inv', {'errores':[error_message]})

        except:
            error_message = "Su solicitud no pudo ser procesada.\nLa informacion introducida es incorrecta."
            return http.request.render('website_self_cfdi_invoice_ee.html_result_error_inv', {'errores':[error_message]})

        return http.request.render('website_self_cfdi_invoice_ee.index',
            {
                'fields': ['RFC','Folio',],
            })
        

class WebsiteAccount(CustomerPortal):

    OPTIONAL_BILLING_FIELDS = ["zipcode", "state_id", "vat", "company_name", "rfc",'uso_cfdi']

