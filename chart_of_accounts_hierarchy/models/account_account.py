from odoo import api, fields, models, _

class AccountAccount(models.Model):
    _inherit = 'account.account'

    parent_id = fields.Many2one('account.account', 'Parent Name')
    child_ids = fields.One2many('account.account', 'parent_id', 'Children')

    @api.model
    def get_coa_hierarchy_info(self):
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
                    'Type' : account.user_type_id.name,
                    'Debit': account.debit,
                    'Credit': account.credit,
                    'Balance': account.balance,
                    'Child_Length' : len(child_ids)
                }                
                datalist.append(vals)

        sorteddatalist = sorted(datalist, key=lambda x: int(x['Child_Length']), reverse=True)

        treedatalist = []
        def PopulateTreeNode(data, ParentID):
            newdata = []            
            for d in data:
                if (d['ParentID'] == ParentID):
                    newdata.append(d)
        
            for d in newdata:
                treedatalist.append(d)
                PopulateTreeNode(data,d['ID'])   
            return treedatalist

        datalist = PopulateTreeNode(sorteddatalist,"0") 

        if datalist:
            return datalist
        else:
            return sorteddatalist