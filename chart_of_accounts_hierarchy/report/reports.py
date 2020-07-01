from odoo import api, models


class COAHierarchyReportPDF(models.AbstractModel):
    _name = 'report.chart_of_accounts_hierarchy.report_coa_hierarchy'

    @api.model
    def _get_report_values(self,docids=None, data=None):
        datalist =[]
        accounts = self.env['account.account'].search([('company_id', '=', self.env.user.company_id.id)])
        if accounts:            
            for account in accounts: 
                balance = 0.0
                credit = 0.0
                debit = 0.0               
                child_ids = self.env['account.account'].search([('id','child_of',[account.id])]).ids
                for line in self.env['account.move.line'].search([('account_id','in',child_ids)]):
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

        pdfdatalist = []
        def PopulateTreeNode(data, ParentID):       
            newdata = []
            for d in data:
                if (d['ParentID'] == ParentID):
                    newdata.append(d)
        
            for d in newdata:
                pdfdatalist.append(d)
                PopulateTreeNode(data,d['ID'])
                    
            return pdfdatalist

        pdfdatalist = PopulateTreeNode(sorteddatalist,"0")

        if pdfdatalist:
            return { 'data': pdfdatalist }
        else:
            return { 'data': sorteddatalist }