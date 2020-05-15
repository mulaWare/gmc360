from odoo import api, fields, models

import urllib.parse
import requests
import datetime

import base64

class SaleOrder(models.Model):
    _inherit = "sale.order"


    sign_template_id = fields.Many2one('sign.template', string="Template")
    sign_reference = fields.Char(string="Filename")
    sign_request_ids = fields.One2many('sign.request', 'template_id', related='sign_template_id.sign_request_ids', string="Signature Requests")


    @api.multi
    def action_cps_send(self):
        '''
        This function opens a window to compose an email, with the edi sale template message loaded by default
        '''
        self.ensure_one()
        pdf = self.env.ref("g360.action_report_cps").render([self.id])[0]

        self.sign_reference = self.name

        attachment = self.env['ir.attachment'].create({
                                        'name': self.sign_reference,
                                        'type': 'binary',
                                        'datas_fname': self.sign_reference + '.pdf',
                                        'datas': base64.encodestring(pdf),
                                        'res_model': 'sale.order',
                                        'res_id': self.id,
                                        'mimetype': 'application/x-pdf'
                                        })
        sign_template_id = self.env['sign.template'].create({'attachment_id': attachment.id, 'favorited_ids': [(4, self.env.user.id)], 'active': True})
        self.sign_template_id = sign_template_id.id
        self.sign_template_id.sale_id = self.id


        sign1_name = self.sign_reference + '_sign1'
        sign1_type_id = self.env['sign.item.type'].search([('type','=','signature')], limit=1)
        sign1_responsible_id = self.env['sign.item.role'].search([], limit=1)
        sign1 = self.env['sign.item'].create({
                                        'template_id': sign_template_id.id,
                                        'name': sign1_name,
                                        'type_id': sign1_type_id.id,
                                        'required': True,
                                        'responsible_id': sign1_responsible_id.id,
                                        'page': 1,
                                        'posX': 0.064,
                                        'posY': 0.648,
                                        'width': 0.2,
                                        'height': 0.05,
                                        })

        sign2_name = self.sign_reference + '_sign2'
        sign2_type_id = self.env['sign.item.type'].search([('type','=','signature')], limit=1)
        sign2_responsible_id = self.env['sign.item.role'].search([], limit=1)
        sign2 = self.env['sign.item'].create({
                                        'template_id': sign_template_id.id,
                                        'name': sign2_name,
                                        'type_id': sign2_type_id.id,
                                        'required': True,
                                        'responsible_id': sign2_responsible_id.id,
                                        'page': 2,
                                        'posX': 0.398,
                                        'posY': 0.513,
                                        'width': 0.2,
                                        'height': 0.05,
                                        })

        sign3_name = self.sign_reference + '_sign3'
        sign3_type_id = self.env['sign.item.type'].search([('type','=','signature')], limit=1)
        sign3_responsible_id = self.env['sign.item.role'].search([], limit=1)
        sign3 = self.env['sign.item'].create({
                                        'template_id': sign_template_id.id,
                                        'name': sign3_name,
                                        'type_id': sign3_type_id.id,
                                        'required': True,
                                        'responsible_id': sign3_responsible_id.id,
                                        'page': 3,
                                        'posX': 0.741,
                                        'posY': 0.095,
                                        'width': 0.2,
                                        'height': 0.05,
                                        })
        return {
            'name': "Template \"%(name)s\"" % {'name': self.sign_template_id.attachment_id.name},
            'type': 'ir.actions.client',
            'tag': 'sign.Template',
            'context': {
                'id': self.sign_template_id.id,
            },
        } 

    @api.multi
    def action_open_sign_request(self):
        self.ensure_one()

        return {
            "type": "ir.actions.act_window",
            "res_model": "sign.request",
            "views": [[False, "form"]],
            "res_id": self.sign_template_id.sign_request_ids.id,
        }
