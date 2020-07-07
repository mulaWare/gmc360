# -*- coding: utf-8 -*-
{
    'name': "Portal de Auto-Facturacion CFDI",

    'summary': """
        Portal de Cliente diseñado para generar facturas desde la Web.""",

    'description': """

Portal Auto-Facturacion CFDI
================================

Permite al Cliente poder generar su Factura mediante la Parte Web.

    """,

    'author': "IT Admin",
    'website': "",
    'category': 'Facturacion Electronica',
    'version': '10.0',
    'depends': [
        'website_sale_stock',
        'website_crm',
        'sale_management',
        'l10n_mx_edi',
        'point_of_sale',
        ],
    'data': [
        'security/ir.model.access.csv',
        'views/templates.xml',
        'views/sale_order_view.xml',
    ],

}
