from odoo import api, fields, models

import urllib.parse
import requests
import datetime

class HrEmployee(models.Model):
    _inherit = "hr.employee"

    alergico = fields.Char(string="Alérgico a:", required=True)
