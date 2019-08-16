from odoo import api, fields, models

import urllib.parse
import requests
import datetime

class SaleOrder(models.Model):
    _inherit = "sale.order"

    fecha_probable = fields.Date(string="Fecha Probable de cierre")
    plazo = fields.Char(string="Plazo")
    anticipo = fields.Char(string="% de anticipo")
    precio_total = fields.Char(string="Precio Total")
    fecha_pago = fields.Date(string="Fecha de Pago")
    pago_total = fields.Char(string="Pago Total")
    pago_contado = fields.Char(string="Pago Contado")
    pago_anticipo = fields.Char(string="Pago Anticipo")
    pago_iguala = fields.Char(string="Pago Iguala")
    nombre = fields.Char(string="Nombre del cliente")
    puesto = fields.Char(string="Puesto del cliente")
    telefono = fields.Char(string="Telefono")
    correo = fields.Char(string="Correo")
    metodo = fields.Selection([
                                ('00','Tranferencia'),
                                ('01','Deposito a cuenta'),
                                ('02','Pago Electronico'),
                                ],
                                string="Metodo de pago", required=False, help="Metodo de pago")

    @api.multi
    def unlink(self):
        for order in self:
            if order.state not in ('draft','cancel','sale',):
                raise UserError(_('You can not delete a sent quotation or a confirmed sales order. You must first cancel it.'))
        return super(SaleOrder, self).unlink()
