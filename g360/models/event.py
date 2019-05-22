# -*- coding: utf-8 -*-

import pytz

from odoo import _, api, fields, models
from odoo.addons.mail.models.mail_template import format_tz
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.translate import html_translate

from dateutil.relativedelta import relativedelta

class EventEvent(models.Model):
    _inherit = "event.event"

    youtube_live = fields.Char(string='YouTube Live URL')
    facebook_live = fields.Char(string='Facebook Live URL')
