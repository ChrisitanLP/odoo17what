from odoo import http
from odoo.http import request

class CombinedController(http.Controller):

    @http.route('/api/combined', auth='public', website=True)
    def list_combined(self, **kwargs):
        products = request.env['product.product'].search([])
        teams = request.env['crm.team'].search([])
        return request.render('whatsapp_message_api.product_and_sales_team_template', {
            'products': products,
            'teams': teams
        })
