# -*- coding: utf-8 -*-
##############################################################################
#
#    ODOO, Open Source Management Solution
#    Copyright (C) 2016 - Today Steigend IT Solutions (Omal Bastin)
#    For more details, check COPYRIGHT and LICENSE files
#
##############################################################################

from odoo import api, models

class AccountChartTemplate(models.Model):
    _inherit = "account.chart.template"
    
    @api.multi
    def generate_account(self, tax_template_ref, acc_template_ref, code_digits, company):
        account_template_account_dict = super(AccountChartTemplate, self).generate_account(tax_template_ref, acc_template_ref, code_digits, company)
        self.update_generated_account(tax_template_ref=tax_template_ref,code_digits=code_digits,
                                      company=company, importing_parent=True)
        return account_template_account_dict
    
    @api.multi
    def update_generated_account(self, tax_template_ref=[], code_digits=1, company=False,importing_parent=False):
        """ This method for generating parent accounts from templates.

            :param tax_template_ref: Taxes templates reference for write taxes_id in account_account.
            :param code_digits: number of digits the accounts code should have in the COA
            :param company: company the wizard is running for
            :returns: return acc_template_ref for reference purpose.
            :rtype: dict
        """
        
        if not importing_parent:
            return True
        self.ensure_one()
        if not company:
            company = self.env.user.company_id
        if company.chart_template_id.id != self.id:
            return True
        
        account_tmpl_obj = self.env['account.account.template'].with_context({'show_parent_account':True})
        account_obj = self.env['account.account'].with_context({'show_parent_account':True})
        acc_templates = account_tmpl_obj.search([('nocreate', '!=', True), ('chart_template_id', '=', self.id),
                                                ], order='id')
        code_account_dict = {}
        
        for account_template in acc_templates:
            tax_ids = []
            for tax in account_template.tax_ids:
                tax_ids.append(tax_template_ref[tax.id])

            code_main = account_template.code and len(account_template.code) or 0
            code_acc = account_template.code or ''
            if code_main > 0 and code_main <= code_digits:
                code_acc =  str(code_acc) + (str('0'*(code_digits-code_main)))
            if account_template.user_type_id.type == 'view':
                new_code = account_template.code
            else:
                new_code = code_acc
            new_account = account_obj.search([('code','=',new_code),
                                              ('company_id','=',company.id)], limit=1)
            if not new_account:
                vals = {
                    'name': account_template.name,
                    'currency_id': account_template.currency_id and account_template.currency_id.id or False,
                    'code':new_code ,
                    'user_type_id': account_template.user_type_id and account_template.user_type_id.id or False,
                    'reconcile': account_template.reconcile,
                    'note': account_template.note,
                    'tax_ids': [(6, 0, tax_ids)],
                    'company_id': company.id,
                    'tag_ids': [(6, 0, [t.id for t in account_template.tag_ids])],
                    'group_id': account_template.group_id.id or False,
                }
                new_account_id = self.create_record_with_xmlid(company, account_template, 'account.account', vals)
                new_account = account_obj.browse(new_account_id)
            if new_code not in code_account_dict:
                code_account_dict[new_code] = new_account
        if company.bank_account_code_prefix:
            if code_account_dict.get(company.bank_account_code_prefix,False):
                parent_account_id = code_account_dict.get(company.bank_account_code_prefix,False)
            else:
                parent_account_id = account_obj.search([
                    ('code','=',company.bank_account_code_prefix),
                    ('user_type_id.type', '=', 'view'),
                    ('company_id','=',company.id)], limit=1)
            account = account_obj.search([('code','like',"%s%%"%company.bank_account_code_prefix),
                                                              ('id','!=',parent_account_id.id),('company_id','=',company.id)])
            account and account.write({'parent_id':parent_account_id.id})
        if company.cash_account_code_prefix:
            if code_account_dict.get(company.cash_account_code_prefix,False):
                parent_account_id = code_account_dict.get(company.cash_account_code_prefix,False)
            else:
                parent_account_id = account_obj.search([
                    ('code','=',company.cash_account_code_prefix),
                    ('user_type_id.type', '=', 'view'),
                    ('company_id','=',company.id)], limit=1)
            
            account = account_obj.search([('code','like',"%s%%"%company.cash_account_code_prefix),
                                          ('id','!=',parent_account_id.id),
                                          ('company_id','=',company.id)])
            account and account.write({'parent_id':parent_account_id.id})
        if company.transfer_account_code_prefix:
            if code_account_dict.get(company.transfer_account_code_prefix,False):
                parent_account_id = code_account_dict.get(company.transfer_account_code_prefix,False)
            else:
                parent_account_id = account_obj.search([
                    ('code','=',company.transfer_account_code_prefix),
                    ('user_type_id.type', '=', 'view'),
                    ('company_id','=',company.id)], limit=1)
            
            account = account_obj.search([('code','like',"%s%%"%company.transfer_account_code_prefix),
                                          ('id','!=',parent_account_id.id),
                                          ('company_id','=',company.id)])
            account and account.write({'parent_id':parent_account_id.id})
        ir_model_data = self.env['ir.model.data']
        for account_template in acc_templates:
            if not account_template.parent_id:
                continue
            template_xml_obj = ir_model_data.search([('model', '=', account_template._name), ('res_id', '=', account_template.id)])
            account_xml_id = "%s.%s_%s" % (template_xml_obj.module, company.id, template_xml_obj.name)
            account = self.env.ref(account_xml_id, raise_if_not_found=False)
            parent_template_xml_obj = ir_model_data.search([('model', '=', account_template._name), ('res_id', '=', account_template.parent_id.id)])
            parent_account_xml_id = "%s.%s_%s" % (parent_template_xml_obj.module, company.id, parent_template_xml_obj.name)
            parent_account = self.env.ref(parent_account_xml_id, raise_if_not_found=False)
            account.write({'parent_id':parent_account.id})
        return True
    