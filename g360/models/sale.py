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
    pago_total = fields.Float(string="Pago Total")
    pago_contado = fields.Float(string="Pago Contado")
    pago_anticipo = fields.Float(string="Pago Anticipo")
    pago_iguala = fields.Char(string="Pago Iguala")
    metodo = fields.Selection([
                                ('00','Tranferencia'),
                                ('01','Deposito a cuenta'),
                                ('02','Pago Electronico'),
                                ],
                                string="Metodo de pago", required=False, help="Metodo de pago")
    nombre = fields.Char(string="Nombre del Tesorero")
    puesto = fields.Char(string="Puesto del Tesorero")
    telefono = fields.Integer(string="Telefono del Tesorero")
    correo = fields.Char(string="Correo del Tesorero")

    @api.multi
    def unlink(self):
        for order in self:
            if order.state not in ('draft','cancel','sale',):
                raise UserError(_('You can not delete a sent quotation or a confirmed sales order. You must first cancel it.'))
        return super(SaleOrder, self).unlink()
