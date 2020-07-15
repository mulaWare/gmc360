# -*- coding: utf-8 -*-
# Copyright 2016 mulaWare - https://mulaware.com/
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Thinkific',
    'version': '12.0.1.0.0',
    'author': 'mulaWare',
    'category': 'Server Tools',
    'website': 'https://mulaware.com',
    'license': 'AGPL-3',
    'depends': [
        'web', 'webhook','sale','product','account',
    ],
    'external_dependencies': {
        'python': [
            'ipaddress',
            'requests',
        ],
    },
    'data': [
        'security/ir.model.access.csv',
        'views/thinkific_views.xml',
        'data/thinkific.xml',
        'data/thinkific_mail_template.xml',
        'data/thinkific_so_email_reminder.xml',               
    ],
    'demo': [

    ],
    'installable': True,
    'auto_install': False,
}
