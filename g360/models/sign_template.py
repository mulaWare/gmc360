# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import re
import base64
import io

from PyPDF2 import PdfFileReader

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import pycompat


class SignTemplate(models.Model):
    _inherit = "sign.template"

    sale_id = fields.Many2one('sale.order', string="Sale Order", required=True, ondelete='cascade')


    @api.model
    def upload_template_sale(self, name=None, dataURL=None, active=True):
        mimetype = dataURL[dataURL.find(':')+1:dataURL.find(',')]
        datas = dataURL[dataURL.find(',')+1:]
        try:
            file_pdf = PdfFileReader(io.BytesIO(base64.b64decode(datas)), strict=False, overwriteWarnings=False)
        except Exception as e:
            raise UserError(_("This file cannot be read. Is it a valid PDF?"))
        if file_pdf.isEncrypted:
            raise UserError(_("Your PDF file shouldn't be encrypted with a password in order to be used as a signature template"))
        attachment = self.env['ir.attachment'].create({'name': name[:name.rfind('.')], 'datas_fname': name, 'datas': datas, 'mimetype': mimetype})
        template = self.create({'attachment_id': attachment.id, 'favorited_ids': [(4, self.env.user.id)], 'active': active})
        return {'template': template.id, 'attachment': attachment.id}
