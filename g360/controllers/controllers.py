# -*- coding: utf-8 -*-
from odoo import http

# class G360(http.Controller):
#     @http.route('/g360/g360/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/g360/g360/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('g360.listing', {
#             'root': '/g360/g360',
#             'objects': http.request.env['g360.g360'].search([]),
#         })

#     @http.route('/g360/g360/objects/<model("g360.g360"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('g360.object', {
#             'object': obj
#         })