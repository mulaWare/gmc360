# -*- coding: utf-8 -*-
##############################################################################
#
#    ODOO, Open Source Management Solution
#    Copyright (C) 2016 - Today Steigend IT Solutions (Omal Bastin)
#    For more details, check COPYRIGHT and LICENSE files
#
##############################################################################
from . import controllers
from . import models
from . import wizard

from odoo import api, SUPERUSER_ID


def _assign_account_parent(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['account.account']._parent_store_compute()
