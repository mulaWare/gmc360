# -*- coding: utf-8 -*-
from odoo import models,fields, api
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime

class DescargaXDiaWizard(models.TransientModel):
    _name ='descarga.x.dia.wizard'
    
    start_date = fields.Date("Fecha de inicio")
    end_date = fields.Date("Fecha Final")
    
    @api.multi
    def download_cfdi_invoices_btw_two_dates(self):
        start_date = self.start_date.strftime(DEFAULT_SERVER_DATE_FORMAT)
        start_date += ' 00:00:00'
        start_date = datetime.strptime(start_date,DEFAULT_SERVER_DATETIME_FORMAT)
        
        end_date = self.end_date.strftime(DEFAULT_SERVER_DATE_FORMAT)
        end_date += ' 23:59:59'
        end_date = datetime.strptime(end_date,DEFAULT_SERVER_DATETIME_FORMAT)
        self.env.user.company_id.download_cfdi_invoices(start_date, end_date)
        return True