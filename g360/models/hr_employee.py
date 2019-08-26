from odoo import api, fields, models

import urllib.parse
import requests
import datetime

class Employee(models.Model):
    _inherit = "hr.employee"

    alergico = fields.Char(string="Alérgico a:", required=False)
