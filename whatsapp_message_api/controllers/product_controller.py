from odoo import http
from odoo.http import request

class ProductController(http.Controller):

    @http.route('/api/products', auth='public', website=True)
    def list_products(self, **kwargs):
        products = request.env['product.product'].search([])
        return request.render('whatsapp_message_api.product_list_template', {'products': products})

    @http.route('/api/info_products', type='json', auth='public', website=False)
    def api_list_products(self):
        products = request.env['product.product'].search([])
        return products.read([
            'id', 'name', 'list_price', 'description', 'default_code',
            'type', 'qty_available','image_1920'
        ])