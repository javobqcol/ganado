# -*- coding: utf-8 -*-
# from odoo import http


# class Garlavaca(http.Controller):
#     @http.route('/ganado/ganado/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ganado/ganado/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('ganado.listing', {
#             'root': '/ganado/ganado',
#             'objects': http.request.env['ganado.ganado'].search([]),
#         })

#     @http.route('/ganado/ganado/objects/<model("ganado.ganado"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ganado.object', {
#             'object': obj
#         })
