# -*- coding: utf-8 -*-

import pytz 

from odoo import _, api, fields, models
from odoo.addons.mail.models.mail_template import format_tz
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.translate import html_translate

from dateutil.relativedelta import relativedelta

class EventEvent(models.Model):
    _inherit = "event.event"
    
    auto_confirm = fields.Boolean(string='Autoconfirm Registrations', default=True)    
    youtube_live = fields.Char(
        string='Youtube Live URL', 
        readonly=False, states={'done': [('readonly', True)]})
    facebook_live = fields.Char(
        string='Facebook Live URL',
        readonly=False, states={'done': [('readonly', True)]})
