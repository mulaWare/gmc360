from odoo import fields, models

import urllib.parse
import requests

class CrmLeadLost(models.TransientModel):
    _inherit = 'crm.lead.lost'

    razon = fields.Text(string="Razón", required=True)
