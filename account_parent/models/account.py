# -*- coding: utf-8 -*-
##############################################################################
#
#    ODOO, Open Source Management Solution
#    Copyright (C) 2016 - Today Steigend IT Solutions (Omal Bastin)
#    For more details, check COPYRIGHT and LICENSE files
#
##############################################################################
from odoo import api, fields, models
import odoo.addons.decimal_precision as dp

class AccountAccountTemplate(models.Model):
    _inherit = "account.account.template"
    
    parent_id = fields.Many2one('account.account.template','Parent Account',ondelete="set null")
    
    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        context = self._context or {}
        if not context.get('show_parent_account',False):
            args += [('user_type_id.type', '!=', 'view')]
        return super(AccountAccountTemplate, self)._search(args, offset=offset, 
                           limit=limit, order=order, count=count,access_rights_uid=access_rights_uid)
        
class AccountAccountType(models.Model):
    _inherit = "account.account.type"
    
    type = fields.Selection(selection_add=[('view','View')])
    

class AccountAccount(models.Model):
    _inherit = "account.account"
    
    @api.multi
    @api.depends('move_line_ids','move_line_ids.amount_currency','move_line_ids.debit','move_line_ids.credit')
    def compute_values(self):
        for account in self:
            sub_accounts = self.with_context({'show_parent_account':True}).search([('id','child_of',[account.id])])
            balance = 0.0
            credit = 0.0
            debit = 0.0
            initial_balance = 0.0
            initial_deb = 0.0
            initial_cre = 0.0
            context = self._context.copy()
            context.update({'account_ids':sub_accounts})
            tables, where_clause, where_params = self.env['account.move.line'].with_context(context)._query_get()
            query1 = 'SELECT account_move_line.debit,account_move_line.credit FROM ' + tables + 'WHERE' + where_clause 
            self.env.cr.execute(query1,tuple(where_params))
            for deb,cre in self.env.cr.fetchall():
                balance += deb - cre
                credit += cre
                debit += deb
            account.balance = balance
            account.credit = credit
            account.debit = debit
            if context.get('show_initial_balance'):
                context.update({'initial_bal': True})
                tables, where_clause, where_params = self.env['account.move.line'].with_context(context)._query_get()
                query2 = 'SELECT account_move_line.debit,account_move_line.credit FROM ' + tables + 'WHERE' + where_clause 
                self.env.cr.execute(query2,tuple(where_params))
                for deb,cre in self.env.cr.fetchall():
                    initial_cre += cre
                    initial_deb += deb
                initial_balance += initial_deb - initial_cre
                account.initial_balance = initial_balance
            else:
                account.initial_balance = 0
    move_line_ids = fields.One2many('account.move.line','account_id','Journal Entry Lines')
    balance = fields.Float(compute="compute_values", digits=dp.get_precision('Account'), string='Balance')
    credit = fields.Float(compute="compute_values",digits=dp.get_precision('Account'), string='Credit')
    debit = fields.Float(compute="compute_values",digits=dp.get_precision('Account'), string='Debit')
    parent_id = fields.Many2one('account.account','Parent Account',ondelete="set null")
    child_ids = fields.One2many('account.account','parent_id', 'Child Accounts')
    parent_path = fields.Char(index=True)
    initial_balance = fields.Float(compute="compute_values", digits=dp.get_precision('Account'), string='Initial Balance')
    
    
    _parent_name = "parent_id"
    _parent_store = True
    _parent_order = 'code, name'
    _order = 'code, id'
    
    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        context = self._context or {}
        if not context.get('show_parent_account',False):
            args += [('user_type_id.type', '!=', 'view')]
        return super(AccountAccount, self)._search(args, offset=offset, 
                           limit=limit, order=order, count=count,access_rights_uid=access_rights_uid)

    
class AccountJournal(models.Model):
    _inherit = "account.journal"
    
    @api.model
    def _prepare_liquidity_account(self, name, company, currency_id, type):
        res = super(AccountJournal, self)._prepare_liquidity_account(name, company, currency_id, type)
        if type == 'bank':
            account_code_prefix = company.bank_account_code_prefix or ''
        else:
            account_code_prefix = company.cash_account_code_prefix or company.bank_account_code_prefix or ''

        parent_id = self.env['account.account'].with_context({'show_parent_account':True}).search([
                                                        ('code','=',account_code_prefix),
                                                        ('company_id','=',company.id),
                                                        ('user_type_id.type','=','view')], limit=1)
        
        if parent_id:
            res.update({'parent_id':parent_id.id})
        return res

