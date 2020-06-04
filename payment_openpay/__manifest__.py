# -*- coding: utf-8 -*-

{
    'name': 'Openpay Payment Acquirer',
    'category': 'Hidden',
    'author': "José Juan Martínez Peláez",
    'support': "contacto@mulaware.com",
    'summary': 'Payment Acquirer: Openpay Implementation',
    'version': '1.0',
    'description': """Openpay Payment Acquirer""",
    'depends': ['payment'],
    'data': [
        'views/payment_views.xml',
        'views/payment_openpay_templates.xml',
        'data/payment_acquirer_data.xml',
    ],
    'images': ['static/description/icon.png'],
    'installable': True,
    'post_init_hook': 'create_missing_journal_for_acquirers',
    'uninstall_hook': 'uninstall_hook',
}
