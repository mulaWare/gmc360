# -*- coding: utf-8 -*-
{
    'name': "GMC360",

    'summary': """
                Customization for GMC360
    """,

    'description': """
        Customization for GMC360
    """,

    'author': "luisvzqz",
    'website': "https://www.gmc360.com.mx",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'addons',
    'version': '0.2',

    # any module necessary for this one to work correctly
    'depends': ['base','account','l10n_mx_edi',],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
      	'views/res_partner_view.xml',        
        'views/views.xml',
        'views/templates.xml',
        'views/payments.xml',        
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
   "installable": True,
   "auto_install": True,
}
