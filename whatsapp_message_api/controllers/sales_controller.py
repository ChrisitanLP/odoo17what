from odoo import http
from odoo.http import request

class SalesTeamController(http.Controller):

    @http.route('/api/sales_team', type='http', auth='public', website=True)
    def list_sales_team(self, **kwargs):
        teams = request.env['crm.team'].search([])
        sales_members = request.env['res.users'].search([('is_sales', '=', True)])
        presales_members = request.env['res.users'].search([('is_presales', '=', True)])
        
        return request.render('whatsapp_message_api.sales_team_template', {
            'teams': teams,
            'sales_members': sales_members,
            'presales_members': presales_members,
        })

    @http.route('/api/info_team', type='json', auth='public', website=False)
    def api_list_sales_team(self):
        teams = request.env['crm.team'].search([])
        return teams.read(['id', 'name'])

    @http.route('/api/sales_members', type='json', auth='public', website=False)
    def api_list_sales_members(self):
        sales_members = request.env['res.users'].search([('is_sales', '=', True)])
        return sales_members.read(['id', 'name', 'email'])

    @http.route('/api/presales_members', type='json', auth='public', website=False)
    def api_list_presales_members(self):
        presales_members = request.env['res.users'].search([('is_presales', '=', True)])
        return presales_members.read(['id', 'name', 'email'])
