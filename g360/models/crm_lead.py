from odoo import fields, models

import urllib.parse
import requests

class Lead(models.Model):
    _inherit = "crm.lead.lost"

    razon = fields.Text(string="Razón", required=True)
