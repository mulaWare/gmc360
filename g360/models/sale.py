from odoo import api, fields, models

import urllib.parse
import requests
import datetime

import base64

class SaleOrder(models.Model):
    _inherit = "sale.order"


    sign_template_id = fields.Many2one('sign.template', string="Template")
    sign_reference = fields.Char(string="Filename")

    @api.multi
    def action_cps_send(self):
        '''
        This function opens a window to compose an email, with the edi sale template message loaded by default
        '''
        self.ensure_one()
        pdf = self.env.ref("g360.action_report_cps").render([self.id])[0]

        self.sign_reference = self.name + '.pdf'

        attachment = self.env['ir.attachment'].create({
                                        'name': self.sign_reference,
                                        'type': 'binary',
                                        'datas': base64.encodestring(pdf),
                                        'res_model': 'sale.order',
                                        'res_id': self.id,
                                        'mimetype': 'application/x-pdf'
                                        })
        sign_template_id = self.env['sign.template'].create({'attachment_id': attachment.id, 'favorited_ids': [(4, self.env.user.id)], 'active': True})
        self.sign_template_id = sign_template_id.id
        self.sign_template_id.sale_id = seld.id 
