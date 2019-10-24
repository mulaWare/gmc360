from odoo import api, fields, models

import urllib.parse
import requests
import datetime

class CrmLost(models.Model):
    _inherit = "crm.lead.lost"

    razon = fields.Text(string="Razón", required=True)
