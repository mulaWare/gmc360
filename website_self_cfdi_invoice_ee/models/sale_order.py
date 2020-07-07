
from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    l10n_mx_edi_payment_method_id = fields.Many2one('l10n_mx_edi.payment.method',
        string='Forma de pago',
        readonly=True,
        states={'draft': [('readonly', False)]},
        help='Indicates the way the invoice was/will be paid, where the '
        'options could be: Cash, Nominal Check, Credit Card, etc. Leave empty '
        'if unkown and the XML will show "Unidentified".',
        default=lambda self: self.env.ref('l10n_mx_edi.payment_method_otros',
                                          raise_if_not_found=False))