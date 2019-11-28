# -*- coding: utf-8 -*-
from openerp import http

# class FinancieraTableroControl(http.Controller):
#     @http.route('/financiera_tablero_control/financiera_tablero_control/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/financiera_tablero_control/financiera_tablero_control/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('financiera_tablero_control.listing', {
#             'root': '/financiera_tablero_control/financiera_tablero_control',
#             'objects': http.request.env['financiera_tablero_control.financiera_tablero_control'].search([]),
#         })

#     @http.route('/financiera_tablero_control/financiera_tablero_control/objects/<model("financiera_tablero_control.financiera_tablero_control"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('financiera_tablero_control.object', {
#             'object': obj
#         })