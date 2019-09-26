# -*- coding: utf-8 -*-

from odoo.addons.web.controllers.main import Action
from odoo import http
from odoo.http import request

#Set company_id variable, so it is accessible in Action domain

class ActionSatSync(Action):
    @http.route()
    def load(self, action_id, additional_context=None):
        value = super(ActionSatSync, self).load(action_id, additional_context)
        if value and value.get('xml_id','')=='l10n_mx_sat_sync_itadmin_ee.action_attachment_cfdi_supplier_invoices':
            try:
                ctx = value.get('context','{}')
                ctx = eval(ctx)
                if 'company_id' not in ctx:
                    ctx.update({'company_id':request.env.user.company_id.id})
                    value['context']=str(ctx)
            except Exception:
                pass
        return value
