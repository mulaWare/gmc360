from odoo import api, fields, models

import urllib.parse
import requests
import datetime

class SaleOrder(models.Model):
    _inherit = "sale.order"

    fecha_probable = fields.Date(string="Fecha Probable de cierre")
    fecha_facturacion = fields.Date(string="Fecha de facturación")
    plazo = fields.Float(string="Plazo")
    anticipo = fields.Float(string="% de anticipo")
    precio_total = fields.Float(string="Precio Total")
    fecha_pago = fields.Date(string="Fecha de Pago")
    pago_iguala = fields.Float(string="Pago Iguala")
    metodo = fields.Selection([
                                ('00','Tranferencia'),
                                ('01','Deposito a cuenta'),
                                ('02','Pago Electronico'),
                                ],
                                string="Metodo de pago", required=False, help="Metodo de pago")
    nombre = fields.Char(string="Nombre del Tesorero")
    puesto = fields.Char(string="Puesto del Tesorero")
    telefono = fields.Char(string="Telefono del Tesorero")
    correo = fields.Char(string="Correo del Tesorero")
    asofich = fields.Boolean(string="ASOFICH")
    amsofipo = fields.Boolean(string="AMSOFIPO")
    asofom = fields.Boolean(string="ASOFOM")

    @api.multi
    def unlink(self):
        #for order in self:
        #    if order.state not in ('draft','cancel','sale',):
        #        raise UserError(_('You can not delete a sent quotation or a confirmed sales order. You must first cancel it.'))
        return super(SaleOrder, self).unlink()

    def erase_public(self):

              for rec in self:
                sale_cr = self.env['sale.order']

                partner = self.env['res.partner'].search([('name','=','Public User')])


                sale_ids = sale_cr.search([('partner_id','=',partner)])

                for sale in sale_ids:
                    if sale:
                        sale.state = 'draft'
                        sale.unlink()
