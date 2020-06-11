# -*- coding: utf-8 -*-
##############################################################################
#
#    ODOO, Open Source Management Solution
#    Copyright (C) 2016 - Today Steigend IT Solutions (Omal Bastin)
#    For more details, check COPYRIGHT and LICENSE files
#
##############################################################################
{
    'name': "Parent Account",
    'summary': """
        Adds Parent account and ability to open chart of account list view based on the date and moves""",
    'description': """
This module will be very useful for those who are still using v7/v8 because of the no parent account and chart of account hierarchy view in the latest versions
        * Adds parent account in account
        * Adds new type 'view' in account type
        * Adds Chart of account hierarchy view
        * Adds credit, debit and balance in account
        * Shows chart of account based on the date and target moves we have selected
        * Provide PDF and XLS reports
    - Need to set the group show chart of account structure to view the chart of account hierarchy.
    
    """,

    'author': 'Steigend IT Solutions',
    'license': 'OPL-1',
    'website': 'http://www.steigendit.com',
    'category': 'Accounting &amp; Finance',
    'version': '12.0.1.3.2',
    'depends': ['account'],
    'data': [
        'security/account_parent_security.xml',
        'views/account_view.xml',
        'views/open_chart.xml',
        'data/account_type_data.xml',
        'views/account_parent_template.xml',
        'views/report_coa_hierarchy.xml',
        'data/fiscal_year_menu.xml'
    ],
    'demo': [
    ],
    'qweb': [
        'static/src/xml/account_parent_backend.xml',
    ],
    'currency': 'EUR',
    'price': '50.0',
    'images': ['static/description/acnt_parent_9.png'],
    'installable': True,
    'post_init_hook': '_assign_account_parent',
}