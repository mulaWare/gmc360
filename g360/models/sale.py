from odoo import api, fields, models

import urllib.parse
import requests
import datetime

class SaleOrder(models.Model):
    _inherit = "sale.order"

    fecha_probable = fields.datetime(string="Fecha Probable de cierre")
