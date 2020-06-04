# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

#  ____________________
# /                    \
# |   DO NOT FORWARD   |
# |    PORT FURTHER    |
# |     THAN 12.4      |
# \____________________/
#          !  !
#          !  !
#          L_ !
#         / _)!
#        / /__L
#  _____/ (____)
#         (____)
#  _____  (____)
#       \_(____)
#          !  !
#          !  !
#          \__/
#
# Starting with 12.5, the payment_openpay module contains these changes OoB

{
    'name': 'Openpay Payment Acquirer - Strong Customer Authentication Update',
    'category': 'Hidden',
    'summary': 'Payment Acquirer: Openpay Implementation for the EU PSD2',
    'version': '1.0',
    'description': """Openpay Payment Acquirer - Strong Customer Authentication Update""",
    'depends': ['payment_openpay'],
    'auto_install': True,
    'data': [
        'views/assets.xml',
        'views/payment_templates.xml',
    ],
    'images': ['static/description/icon.png'],
}
