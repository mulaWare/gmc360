# Copyright 2017 LasLabs Inc.
# Copyright 2018 ACSONE SA/NV.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import timedelta
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError



class ContractLine(models.Model):
    _inherit = 'contract.line'


    last_date_invoiced = fields.Date(
        string='Last Date Invoiced', readonly=False, copy=False
    )
