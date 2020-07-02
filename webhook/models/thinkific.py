# -*- coding: utf-8 -*-
# Copyright 2016 Vauxoo - https://www.vauxoo.com/
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json
import requests
import pprint

from odoo.tests.common import HttpCase
from odoo import api, exceptions, tools, models
from odoo.tools.translate import _


HOST = '127.0.0.1'
#PORT = tools.config['xmlrpc_port']
PORT = '8069'

class Webhook(models.Model):
    _inherit = 'webhook'

    last_request = fields.Text(string="Last Request")

    @api.multi
    def run_thinkific_order_created(self):
        self.ensure_one()
        self.last_request = self.env.request.jsonrequest['resource']
        pprint.pformat(self.env.request.jsonrequest)[:450]
        if self.env.request.jsonrequest['foo'] != 'bar':
            raise exceptions.ValidationError(_("Wrong value received"))
