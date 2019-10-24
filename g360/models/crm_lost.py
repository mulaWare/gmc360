from odoo import fields, models

import urllib.parse
import requests

class Crm(models.Model):
    _inherit = "crm.lead.lost.form"

    razon = fields.Text(string="Razón", required=True)
