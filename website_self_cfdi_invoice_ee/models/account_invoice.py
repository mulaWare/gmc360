

from odoo import models, api, fields

class AccountInvoice(models.Model):
    _inherit='account.invoice'

    self_invoice = fields.Boolean('Self invoice', default=False)

    @api.multi
    def force_invoice_send(self):
        for inv in self:
            email_act = inv.action_invoice_sent()
            if email_act and email_act.get('context'):
                email_ctx = email_act['context']
                email_ctx.update(default_email_from=inv.company_id.email)
                inv.with_context(email_ctx).message_post_with_template(email_ctx.get('default_template_id'))
        return True

    @api.multi
    def _l10n_mx_edi_post_sign_process(self, xml_signed, code=None, msg=None):
        res = super(AccountInvoice, self)._l10n_mx_edi_post_sign_process(xml_signed, code=code, msg=msg)
        if self.self_invoice:
            self.force_invoice_send()
            self.self_invoice = False
        return res
      
    @api.multi
    def invoice_validate(self):
        res  = super(AccountInvoice, self).invoice_validate()
        #attachment_obj = self.env['ir.attachment']
        for invoice in self:
            self.env.cr.execute("delete from ir_attachment where name like 'Invoice_%s' and res_id = %s and res_model='account.invoice';" % ('%',invoice.id,))
        return res
