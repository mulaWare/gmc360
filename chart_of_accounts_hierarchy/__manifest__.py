# -*- coding: utf-8 -*-
#################################################################################
# Author      : CodersFort (<https://codersfort.com/>)
# Copyright(c): 2017-Present CodersFort.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://codersfort.com/>
#################################################################################

{
    "name": "Chart of Accounts Hierarchy (Chart of Account Hierarchy)",
    "summary": "Chart of Accounts Hierarchy",
    "version": "12.0.1",
    "description": """Chart of accounts hierarchy defines how accounts are related to each other, 
        This module will adds the parent id of each Account and bulid tree structure relation between Accounts Visually.""",    
    "author": "Ananthu Krishna",
    "maintainer": "Ananthu Krishna",
    "license" :  "Other proprietary",
    "website": "http://www.codersfort.com",
    "images": ["images/chart_of_accounts_hierarchy.png"],
    "category": "Accounting Management",
    "depends": ["account"],
    "data": [
        'views/assets.xml',
        'views/account_views.xml',
        'report/coa_hierarchy_templates.xml',
        'report/reports.xml',
    ],
    "qweb": ["static/src/xml/chart_of_accounts_hierarchy.xml"],
    "installable": True,
    "application": True,
    "price"                :  35,
    "currency"             :  "EUR",
    "pre_init_hook"        :  "pre_init_check",   
}
