from odoo import http
from odoo.http import request
from odoo.tools import ustr
from odoo.tools.misc import xlwt

import io
import base64

class COAHiearchyExporter(http.Controller):

    @http.route('/coa_export_xls', type='http', auth="user")
    def export_xls(self,token=None):
        datalist =[]
        accounts = request.env['account.account'].sudo().search([('company_id', '=', request.env.user.company_id.id)])
        if accounts:            
            for account in accounts: 
                balance = 0.0
                credit = 0.0
                debit = 0.0               
                child_ids = request.env['account.account'].sudo().search([('id','child_of',[account.id])]).ids
                for line in request.env['account.move.line'].sudo().search([('account_id','in',child_ids)]):
                    balance += line.debit - line.credit
                    credit += line.credit
                    debit += line.debit

                account.balance = balance
                account.credit = credit
                account.debit = debit
                
                vals = {
                    'ID' : account.id,
                    'ParentID' : account.parent_id.id if account.parent_id.id else "0",
                    'Name' : account.name,
                    'Code' : account.code,
                    'Parent Code' : account.parent_id.code,
                    'Type' : account.user_type_id.name,
                    'Debit': account.debit,
                    'Credit': account.credit,
                    'Balance': account.balance,
                    'Child_Length' : len(child_ids),
                }
                datalist.append(vals)

        sorteddatalist = sorted(datalist, key=lambda x: int(x['Child_Length']), reverse=True)
        xlsxdatalist = []
        def PopulateTreeNode(data, ParentID):       
            newdata = []
            for d in data:
                if (d['ParentID'] == ParentID):
                    newdata.append(d)
        
            for d in newdata:
                xlsxdatalist.append(d)
                PopulateTreeNode(data,d['ID'])
                    
            return xlsxdatalist

        xlsxdatalist = PopulateTreeNode(sorteddatalist,"0")

        if xlsxdatalist: 
            workbook = xlwt.Workbook()
            sheet = workbook.add_sheet('COA Hierarchy')

            normal = xlwt.easyxf('font: name Times New Roman ;align: horiz left;', num_format_str='#,##0.00')            
            bold = xlwt.easyxf('font: name Times New Roman bold ;align: horiz left;', num_format_str='#,##0.00')            

            sheet.write(0, 0,'Code', bold)
            sheet.write(0, 1,'Parent Code', bold)
            sheet.write(0, 2,'Name', bold)
            sheet.write(0, 3,'Type', bold)
            sheet.write(0, 4,'Debit', bold)
            sheet.write(0, 5,'Credit', bold)
            sheet.write(0, 6,'Balance', bold)

            i = 1
                        
            for data in xlsxdatalist:
                sheet.write(i, 0, data['Code'] or '', normal)
                sheet.write(i, 1, data['Parent Code'] or '0', normal)
                sheet.write(i, 2, data['Name'] or '', normal)
                sheet.write(i, 3, data['Type'] or '', normal)
                sheet.write(i, 4, data['Debit'] or '0', normal)
                sheet.write(i, 5, data['Credit'] or '0', normal)
                sheet.write(i, 6, data['Balance'] or '0', normal)            
                i += 1  

            fp = io.BytesIO()
            workbook.save(fp)
            data = fp.getvalue()
            fp.close()

            response = request.make_response(data,
                headers=[('Content-Type', 'application/vnd.ms-excel'),
                        ('Content-Disposition', 'attachment; filename=coahiearchy.xls')],
                cookies={'fileToken': token})
            return response