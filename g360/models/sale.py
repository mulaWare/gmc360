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
    def action_cps_int_send(self):
        '''
        This function opens a window to compose an email, with the edi sale template message loaded by default
        '''
        self.ensure_one()
        pdf = self.env.ref("g360.action_report_cps_integral").render([self.id])[0]

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
                                        'posX': 0.782,
                                        'posY': 0.931,
                                        'width': 0.200,
                                        'height': 0.050,
                                        })

        sign2_name = self.sign_reference + '_sign2'
        sign2_type_id = self.env['sign.item.type'].search([('type','=','text')], limit=1)
        sign2_responsible_id = self.env['sign.item.role'].search([], limit=1)
        sign2 = self.env['sign.item'].create({
                                        'template_id': sign_template_id.id,
                                        'name': sign2_name,
                                        'type_id': sign2_type_id.id,
                                        'required': True,
                                        'responsible_id': sign2_responsible_id.id,
                                        'page': 2,
                                        'posX': 0.134,
                                        'posY': 0.300,
                                        'width': 0.060,
                                        'height': 0.013,
                                        })

        sign3_name = self.sign_reference + '_sign3'
        sign3_type_id = self.env['sign.item.type'].search([('type','=','text')], limit=1)
        sign3_responsible_id = self.env['sign.item.role'].search([], limit=1)
        sign3 = self.env['sign.item'].create({
                                        'template_id': sign_template_id.id,
                                        'name': sign3_name,
                                        'type_id': sign3_type_id.id,
                                        'required': True,
                                        'responsible_id': sign3_responsible_id.id,
                                        'page': 2,
                                        'posX': 0.056,
                                        'posY': 0.300,
                                        'width': 0.060,
                                        'height': 0.013,
                                        })

        sign4_name = self.sign_reference + '_sign4'
        sign4_type_id = self.env['sign.item.type'].search([('type','=','text')], limit=1)
        sign4_responsible_id = self.env['sign.item.role'].search([], limit=1)
        sign4 = self.env['sign.item'].create({
                                        'template_id': sign_template_id.id,
                                        'name': sign4_name,
                                        'type_id': sign4_type_id.id,
                                        'required': True,
                                        'responsible_id': sign4_responsible_id.id,
                                        'page': 2,
                                        'posX': 0.850,
                                        'posY': 0.300,
                                        'width': 0.101,
                                        'height': 0.013,
                                        })

        sign5_name = self.sign_reference + '_sign5'
        sign5_type_id = self.env['sign.item.type'].search([('type','=','text')], limit=1)
        sign5_responsible_id = self.env['sign.item.role'].search([], limit=1)
        sign5 = self.env['sign.item'].create({
                                        'template_id': sign_template_id.id,
                                        'name': sign5_name,
                                        'type_id': sign5_type_id.id,
                                        'required': True,
                                        'responsible_id': sign5_responsible_id.id,
                                        'page': 2,
                                        'posX': 0.680,
                                        'posY': 0.300,
                                        'width': 0.056,
                                        'height': 0.013,
                                        })

        sign6_name = self.sign_reference + '_sign6'
        sign6_type_id = self.env['sign.item.type'].search([('type','=','text')], limit=1)
        sign6_responsible_id = self.env['sign.item.role'].search([], limit=1)
        sign6 = self.env['sign.item'].create({
                                        'template_id': sign_template_id.id,
                                        'name': sign6_name,
                                        'type_id': sign6_type_id.id,
                                        'required': True,
                                        'responsible_id': sign6_responsible_id.id,
                                        'page': 2,
                                        'posX': 0.194,
                                        'posY': 0.300,
                                        'width': 0.097,
                                        'height': 0.013,
                                        })

        sign7_name = self.sign_reference + '_sign7'
        sign7_type_id = self.env['sign.item.type'].search([('type','=','text')], limit=1)
        sign7_responsible_id = self.env['sign.item.role'].search([], limit=1)
        sign7 = self.env['sign.item'].create({
                                        'template_id': sign_template_id.id,
                                        'name': sign7_name,
                                        'type_id': sign7_type_id.id,
                                        'required': True,
                                        'responsible_id': sign7_responsible_id.id,
                                        'page': 2,
                                        'posX': 0.292,
                                        'posY': 0.300,
                                        'width': 0.059,
                                        'height': 0.013,
                                        })

        sign8_name = self.sign_reference + '_sign8'
        sign8_type_id = self.env['sign.item.type'].search([('type','=','text')], limit=1)
        sign8_responsible_id = self.env['sign.item.role'].search([], limit=1)
        sign8 = self.env['sign.item'].create({
                                        'template_id': sign_template_id.id,
                                        'name': sign8_name,
                                        'type_id': sign8_type_id.id,
                                        'required': True,
                                        'responsible_id': sign8_responsible_id.id,
                                        'page': 2,
                                        'posX': 0.581,
                                        'posY': 0.300,
                                        'width': 0.098,
                                        'height': 0.013,
                                        })

        sign9_name = self.sign_reference + '_sign9'
        sign9_type_id = self.env['sign.item.type'].search([('type','=','text')], limit=1)
        sign9_responsible_id = self.env['sign.item.role'].search([], limit=1)
        sign9 = self.env['sign.item'].create({
                                        'template_id': sign_template_id.id,
                                        'name': sign9_name,
                                        'type_id': sign9_type_id.id,
                                        'required': True,
                                        'responsible_id': sign9_responsible_id.id,
                                        'page': 2,
                                        'posX': 0.740,
                                        'posY': 0.300,
                                        'width': 0.112,
                                        'height': 0.013,
                                        })

        sign10_name = self.sign_reference + '_sign10'
        sign10_type_id = self.env['sign.item.type'].search([('type','=','text')], limit=1)
        sign10_responsible_id = self.env['sign.item.role'].search([], limit=1)
        sign10 = self.env['sign.item'].create({
                                        'template_id': sign_template_id.id,
                                        'name': sign10_name,
                                        'type_id': sign10_type_id.id,
                                        'required': True,
                                        'responsible_id': sign10_responsible_id.id,
                                        'page': 2,
                                        'posX': 0.352,
                                        'posY': 0.300,
                                        'width': 0.138,
                                        'height': 0.013,
                                        })

        sign11_name = self.sign_reference + '_sign11'
        sign11_type_id = self.env['sign.item.type'].search([('type','=','text')], limit=1)
        sign11_responsible_id = self.env['sign.item.role'].search([], limit=1)
        sign11 = self.env['sign.item'].create({
                                        'template_id': sign_template_id.id,
                                        'name': sign11_name,
                                        'type_id': sign11_type_id.id,
                                        'required': True,
                                        'responsible_id': sign11_responsible_id.id,
                                        'page': 2,
                                        'posX': 0.492,
                                        'posY': 0.300,
                                        'width': 0.138,
                                        'height': 0.013,
                                        })

        sign12_name = self.sign_reference + '_sign12'
        sign12_type_id = self.env['sign.item.type'].search([('type','=','text')], limit=1)
        sign12_responsible_id = self.env['sign.item.role'].search([], limit=1)
        sign12 = self.env['sign.item'].create({
                                        'template_id': sign_template_id.id,
                                        'name': sign12_name,
                                        'type_id': sign12_type_id.id,
                                        'required': True,
                                        'responsible_id': sign12_responsible_id.id,
                                        'page': 2,
                                        'posX': 0.580,
                                        'posY': 0.368,
                                        'width': 0.100,
                                        'height': 0.013,
                                        })

        sign13_name = self.sign_reference + '_sign13'
        sign13_type_id = self.env['sign.item.type'].search([('type','=','text')], limit=1)
        sign13_responsible_id = self.env['sign.item.role'].search([], limit=1)
        sign13 = self.env['sign.item'].create({
                                        'template_id': sign_template_id.id,
                                        'name': sign13_name,
                                        'type_id': sign13_type_id.id,
                                        'required': True,
                                        'responsible_id': sign13_responsible_id.id,
                                        'page': 2,
                                        'posX': 0.681,
                                        'posY': 0.368,
                                        'width': 0.056,
                                        'height': 0.013,
                                        })

        sign14_name = self.sign_reference + '_sign14'
        sign14_type_id = self.env['sign.item.type'].search([('type','=','text')], limit=1)
        sign14_responsible_id = self.env['sign.item.role'].search([], limit=1)
        sign14 = self.env['sign.item'].create({
                                        'template_id': sign_template_id.id,
                                        'name': sign14_name,
                                        'type_id': sign14_type_id.id,
                                        'required': True,
                                        'responsible_id': sign14_responsible_id.id,
                                        'page': 2,
                                        'posX': 0.293,
                                        'posY': 0.368,
                                        'width': 0.057,
                                        'height': 0.013,
                                        })

        sign15_name = self.sign_reference + '_sign15'
        sign15_type_id = self.env['sign.item.type'].search([('type','=','text')], limit=1)
        sign15_responsible_id = self.env['sign.item.role'].search([], limit=1)
        sign15 = self.env['sign.item'].create({
                                        'template_id': sign_template_id.id,
                                        'name': sign15_name,
                                        'type_id': sign15_type_id.id,
                                        'required': True,
                                        'responsible_id': sign15_responsible_id.id,
                                        'page': 2,
                                        'posX': 0.352,
                                        'posY': 0.368,
                                        'width': 0.140,
                                        'height': 0.013,
                                        })

        sign16_name = self.sign_reference + '_sign16'
        sign16_type_id = self.env['sign.item.type'].search([('type','=','text')], limit=1)
        sign16_responsible_id = self.env['sign.item.role'].search([], limit=1)
        sign16 = self.env['sign.item'].create({
                                        'template_id': sign_template_id.id,
                                        'name': sign16_name,
                                        'type_id': sign16_type_id.id,
                                        'required': True,
                                        'responsible_id': sign16_responsible_id.id,
                                        'page': 2,
                                        'posX': 0.739,
                                        'posY': 0.368,
                                        'width': 0.110,
                                        'height': 0.013,
                                        })

        sign17_name = self.sign_reference + '_sign17'
        sign17_type_id = self.env['sign.item.type'].search([('type','=','text')], limit=1)
        sign17_responsible_id = self.env['sign.item.role'].search([], limit=1)
        sign17 = self.env['sign.item'].create({
                                        'template_id': sign_template_id.id,
                                        'name': sign17_name,
                                        'type_id': sign17_type_id.id,
                                        'required': True,
                                        'responsible_id': sign17_responsible_id.id,
                                        'page': 2,
                                        'posX': 0.194,
                                        'posY': 0.368,
                                        'width': 0.100,
                                        'height': 0.013,
                                        })

        sign18_name = self.sign_reference + '_sign18'
        sign18_type_id = self.env['sign.item.type'].search([('type','=','text')], limit=1)
        sign18_responsible_id = self.env['sign.item.role'].search([], limit=1)
        sign18 = self.env['sign.item'].create({
                                        'template_id': sign_template_id.id,
                                        'name': sign18_name,
                                        'type_id': sign18_type_id.id,
                                        'required': True,
                                        'responsible_id': sign18_responsible_id.id,
                                        'page': 2,
                                        'posX': 0.850,
                                        'posY': 0.368,
                                        'width': 0.098,
                                        'height': 0.013,
                                        })

        sign19_name = self.sign_reference + '_sign19'
        sign19_type_id = self.env['sign.item.type'].search([('type','=','text')], limit=1)
        sign19_responsible_id = self.env['sign.item.role'].search([], limit=1)
        sign19 = self.env['sign.item'].create({
                                        'template_id': sign_template_id.id,
                                        'name': sign19_name,
                                        'type_id': sign19_type_id.id,
                                        'required': True,
                                        'responsible_id': sign19_responsible_id.id,
                                        'page': 2,
                                        'posX': 0.492,
                                        'posY': 0.368,
                                        'width': 0.086,
                                        'height': 0.013,
                                        })

        sign20_name = self.sign_reference + '_sign20'
        sign20_type_id = self.env['sign.item.type'].search([('type','=','checkbox')], limit=1)
        sign20_responsible_id = self.env['sign.item.role'].search([], limit=1)
        sign20 = self.env['sign.item'].create({
                                        'template_id': sign_template_id.id,
                                        'name': sign20_name,
                                        'type_id': sign20_type_id.id,
                                        'required': True,
                                        'responsible_id': sign20_responsible_id.id,
                                        'page': 2,
                                        'posX': 0.171,
                                        'posY': 0.368,
                                        'width': 0.015,
                                        'height': 0.013,
                                        })

        sign21_name = self.sign_reference + '_sign21'
        sign21_type_id = self.env['sign.item.type'].search([('type','=','checkbox')], limit=1)
        sign21_responsible_id = self.env['sign.item.role'].search([], limit=1)
        sign21 = self.env['sign.item'].create({
                                        'template_id': sign_template_id.id,
                                        'name': sign21_name,
                                        'type_id': sign21_type_id.id,
                                        'required': True,
                                        'responsible_id': sign21_responsible_id.id,
                                        'page': 2,
                                        'posX': 0.099,
                                        'posY': 0.368,
                                        'width': 0.015,
                                        'height': 0.013,
                                        })

        sign22_name = self.sign_reference + '_sign22'
        sign22_type_id = self.env['sign.item.type'].search([('type','=','text')], limit=1)
        sign22_responsible_id = self.env['sign.item.role'].search([], limit=1)
        sign22 = self.env['sign.item'].create({
                                        'template_id': sign_template_id.id,
                                        'name': sign22_name,
                                        'type_id': sign22_type_id.id,
                                        'required': True,
                                        'responsible_id': sign22_responsible_id.id,
                                        'page': 2,
                                        'posX': 0.164,
                                        'posY': 0.585,
                                        'width': 0.416,
                                        'height': 0.013,
                                        })

        sign23_name = self.sign_reference + '_sign23'
        sign23_type_id = self.env['sign.item.type'].search([('type','=','text')], limit=1)
        sign23_responsible_id = self.env['sign.item.role'].search([], limit=1)
        sign23 = self.env['sign.item'].create({
                                        'template_id': sign_template_id.id,
                                        'name': sign23_name,
                                        'type_id': sign23_type_id.id,
                                        'required': True,
                                        'responsible_id': sign23_responsible_id.id,
                                        'page': 2,
                                        'posX': 0.738,
                                        'posY': 0.585,
                                        'width': 0.206,
                                        'height': 0.013,
                                        })

        sign24_name = self.sign_reference + '_sign24'
        sign24_type_id = self.env['sign.item.type'].search([('type','=','text')], limit=1)
        sign24_responsible_id = self.env['sign.item.role'].search([], limit=1)
        sign24 = self.env['sign.item'].create({
                                        'template_id': sign_template_id.id,
                                        'name': sign24_name,
                                        'type_id': sign24_type_id.id,
                                        'required': True,
                                        'responsible_id': sign24_responsible_id.id,
                                        'page': 2,
                                        'posX': 0.134,
                                        'posY': 0.585,
                                        'width': 0.061,
                                        'height': 0.013,
                                        })

        sign25_name = self.sign_reference + '_sign25'
        sign25_type_id = self.env['sign.item.type'].search([('type','=','text')], limit=1)
        sign25_responsible_id = self.env['sign.item.role'].search([], limit=1)
        sign25 = self.env['sign.item'].create({
                                        'template_id': sign_template_id.id,
                                        'name': sign25_name,
                                        'type_id': sign25_type_id.id,
                                        'required': True,
                                        'responsible_id': sign25_responsible_id.id,
                                        'page': 2,
                                        'posX': 0.055,
                                        'posY': 0.585,
                                        'width': 0.076,
                                        'height': 0.013,
                                        })

        sign26_name = self.sign_reference + '_sign26'
        sign26_type_id = self.env['sign.item.type'].search([('type','=','text')], limit=1)
        sign26_responsible_id = self.env['sign.item.role'].search([], limit=1)
        sign26 = self.env['sign.item'].create({
                                        'template_id': sign_template_id.id,
                                        'name': sign26_name,
                                        'type_id': sign26_type_id.id,
                                        'required': True,
                                        'responsible_id': sign26_responsible_id.id,
                                        'page': 2,
                                        'posX': 0.850,
                                        'posY': 0.673,
                                        'width': 0.098,
                                        'height': 0.013,
                                        })

        sign27_name = self.sign_reference + '_sign27'
        sign27_type_id = self.env['sign.item.type'].search([('type','=','text')], limit=1)
        sign27_responsible_id = self.env['sign.item.role'].search([], limit=1)
        sign27 = self.env['sign.item'].create({
                                        'template_id': sign_template_id.id,
                                        'name': sign27_name,
                                        'type_id': sign27_type_id.id,
                                        'required': True,
                                        'responsible_id': sign27_responsible_id.id,
                                        'page': 2,
                                        'posX': 0.293,
                                        'posY': 0.673,
                                        'width': 0.057,
                                        'height': 0.013,
                                        })

        sign28_name = self.sign_reference + '_sign28'
        sign28_type_id = self.env['sign.item.type'].search([('type','=','text')], limit=1)
        sign28_responsible_id = self.env['sign.item.role'].search([], limit=1)
        sign28 = self.env['sign.item'].create({
                                        'template_id': sign_template_id.id,
                                        'name': sign28_name,
                                        'type_id': sign28_type_id.id,
                                        'required': True,
                                        'responsible_id': sign28_responsible_id.id,
                                        'page': 2,
                                        'posX': 0.196,
                                        'posY': 0.673,
                                        'width': 0.096,
                                        'height': 0.013,
                                        })

        sign29_name = self.sign_reference + '_sign29'
        sign29_type_id = self.env['sign.item.type'].search([('type','=','text')], limit=1)
        sign29_responsible_id = self.env['sign.item.role'].search([], limit=1)
        sign29 = self.env['sign.item'].create({
                                        'template_id': sign_template_id.id,
                                        'name': sign29_name,
                                        'type_id': sign29_type_id.id,
                                        'required': True,
                                        'responsible_id': sign29_responsible_id.id,
                                        'page': 2,
                                        'posX': 0.738,
                                        'posY': 0.673,
                                        'width': 0.114,
                                        'height': 0.013,
                                        })

        sign30_name = self.sign_reference + '_sign30'
        sign30_type_id = self.env['sign.item.type'].search([('type','=','text')], limit=1)
        sign30_responsible_id = self.env['sign.item.role'].search([], limit=1)
        sign30 = self.env['sign.item'].create({
                                        'template_id': sign_template_id.id,
                                        'name': sign30_name,
                                        'type_id': sign30_type_id.id,
                                        'required': True,
                                        'responsible_id': sign30_responsible_id.id,
                                        'page': 2,
                                        'posX': 0.492,
                                        'posY': 0.673,
                                        'width': 0.087,
                                        'height': 0.013,
                                        })

        sign31_name = self.sign_reference + '_sign31'
        sign31_type_id = self.env['sign.item.type'].search([('type','=','text')], limit=1)
        sign31_responsible_id = self.env['sign.item.role'].search([], limit=1)
        sign31 = self.env['sign.item'].create({
                                        'template_id': sign_template_id.id,
                                        'name': sign31_name,
                                        'type_id': sign31_type_id.id,
                                        'required': True,
                                        'responsible_id': sign31_responsible_id.id,
                                        'page': 2,
                                        'posX': 0.579,
                                        'posY': 0.673,
                                        'width': 0.100,
                                        'height': 0.013,
                                        })

        sign32_name = self.sign_reference + '_sign32'
        sign32_type_id = self.env['sign.item.type'].search([('type','=','text')], limit=1)
        sign32_responsible_id = self.env['sign.item.role'].search([], limit=1)
        sign32 = self.env['sign.item'].create({
                                        'template_id': sign_template_id.id,
                                        'name': sign32_name,
                                        'type_id': sign32_type_id.id,
                                        'required': True,
                                        'responsible_id': sign32_responsible_id.id,
                                        'page': 2,
                                        'posX': 0.680,
                                        'posY': 0.673,
                                        'width': 0.056,
                                        'height': 0.013,
                                        })

        sign33_name = self.sign_reference + '_sign33'
        sign33_type_id = self.env['sign.item.type'].search([('type','=','text')], limit=1)
        sign33_responsible_id = self.env['sign.item.role'].search([], limit=1)
        sign33 = self.env['sign.item'].create({
                                        'template_id': sign_template_id.id,
                                        'name': sign33_name,
                                        'type_id': sign33_type_id.id,
                                        'required': True,
                                        'responsible_id': sign33_responsible_id.id,
                                        'page': 2,
                                        'posX': 0.350,
                                        'posY': 0.673,
                                        'width': 0.141,
                                        'height': 0.013,
                                        })

        sign34_name = self.sign_reference + '_sign34'
        sign34_type_id = self.env['sign.item.type'].search([('type','=','signature')], limit=1)
        sign34_responsible_id = self.env['sign.item.role'].search([], limit=1)
        sign34 = self.env['sign.item'].create({
                                        'template_id': sign_template_id.id,
                                        'name': sign34_name,
                                        'type_id': sign34_type_id.id,
                                        'required': True,
                                        'responsible_id': sign34_responsible_id.id,
                                        'page': 2,
                                        'posX': 0.796,
                                        'posY': 0.881,
                                        'width': 0.200,
                                        'height': 0.050,
                                        })



        sign36_name = self.sign_reference + '_sign36'
        sign36_type_id = self.env['sign.item.type'].search([('type','=','signature')], limit=1)
        sign36_responsible_id = self.env['sign.item.role'].search([], limit=1)
        sign36 = self.env['sign.item'].create({
                                        'template_id': sign_template_id.id,
                                        'name': sign36_name,
                                        'type_id': sign36_type_id.id,
                                        'required': True,
                                        'responsible_id': sign36_responsible_id.id,
                                        'page': 3,
                                        'posX': 0.754,
                                        'posY': 0.943,
                                        'width': 0.200,
                                        'height': 0.050,
                                        })

        sign37_name = self.sign_reference + '_sign37'
        sign37_type_id = self.env['sign.item.type'].search([('type','=','signature')], limit=1)
        sign37_responsible_id = self.env['sign.item.role'].search([], limit=1)
        sign37 = self.env['sign.item'].create({
                                        'template_id': sign_template_id.id,
                                        'name': sign37_name,
                                        'type_id': sign37_type_id.id,
                                        'required': True,
                                        'responsible_id': sign37_responsible_id.id,
                                        'page': 4,
                                        'posX': 0.057,
                                        'posY': 0.634,
                                        'width': 0.200,
                                        'height': 0.050,
                                        })

        sign38_name = self.sign_reference + '_sign38'
        sign38_type_id = self.env['sign.item.type'].search([('type','=','signature')], limit=1)
        sign38_responsible_id = self.env['sign.item.role'].search([], limit=1)
        sign38 = self.env['sign.item'].create({
                                        'template_id': sign_template_id.id,
                                        'name': sign38_name,
                                        'type_id': sign38_type_id.id,
                                        'required': True,
                                        'responsible_id': sign38_responsible_id.id,
                                        'page': 5,
                                        'posX': 0.774,
                                        'posY': 0.944,
                                        'width': 0.200,
                                        'height': 0.050,
                                        })

        sign39_name = self.sign_reference + '_sign39'
        sign39_type_id = self.env['sign.item.type'].search([('type','=','signature')], limit=1)
        sign39_responsible_id = self.env['sign.item.role'].search([], limit=1)
        sign39 = self.env['sign.item'].create({
                                        'template_id': sign_template_id.id,
                                        'name': sign39_name,
                                        'type_id': sign39_type_id.id,
                                        'required': True,
                                        'responsible_id': sign39_responsible_id.id,
                                        'page': 6,
                                        'posX': 0.060,
                                        'posY': 0.247,
                                        'width': 0.200,
                                        'height': 0.050,
                                        })

        sign40_name = self.sign_reference + '_sign40'
        sign40_type_id = self.env['sign.item.type'].search([('type','=','signature')], limit=1)
        sign40_responsible_id = self.env['sign.item.role'].search([], limit=1)
        sign40 = self.env['sign.item'].create({
                                        'template_id': sign_template_id.id,
                                        'name': sign40_name,
                                        'type_id': sign40_type_id.id,
                                        'required': True,
                                        'responsible_id': sign40_responsible_id.id,
                                        'page': 7,
                                        'posX': 0.770,
                                        'posY': 0.944,
                                        'width': 0.200,
                                        'height': 0.050,
                                        })

        sign41_name = self.sign_reference + '_sign41'
        sign41_type_id = self.env['sign.item.type'].search([('type','=','signature')], limit=1)
        sign41_responsible_id = self.env['sign.item.role'].search([], limit=1)
        sign41 = self.env['sign.item'].create({
                                        'template_id': sign_template_id.id,
                                        'name': sign41_name,
                                        'type_id': sign41_type_id.id,
                                        'required': True,
                                        'responsible_id': sign41_responsible_id.id,
                                        'page': 8,
                                        'posX': 0.057,
                                        'posY': 0.289,
                                        'width': 0.200,
                                        'height': 0.050,
                                        })

        sign42_name = self.sign_reference + '_sign42'
        sign42_type_id = self.env['sign.item.type'].search([('type','=','signature')], limit=1)
        sign42_responsible_id = self.env['sign.item.role'].search([], limit=1)
        sign42 = self.env['sign.item'].create({
                                        'template_id': sign_template_id.id,
                                        'name': sign42_name,
                                        'type_id': sign42_type_id.id,
                                        'required': True,
                                        'responsible_id': sign42_responsible_id.id,
                                        'page': 9,
                                        'posX': 0.731,
                                        'posY': 0.071,
                                        'width': 0.200,
                                        'height': 0.050,
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
