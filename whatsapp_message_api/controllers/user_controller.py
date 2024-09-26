from odoo import http
from odoo.http import request, Response
import logging
import json

_logger = logging.getLogger(__name__)

class WhatsappUserController(http.Controller):

    @http.route('/api/user/initial_load', type='http', auth='public')
    def initial_load(self):
        """Endpoint para iniciar la carga inicial de datos del usuario de WhatsApp."""
        try:
            whatsapp_user_model = request.env['whatsapp_message_api.whatsapp_user']
            whatsapp_user_model.initial_load()
            response_data = {
                'status': 'success', 
                'message': 'Carga inicial de Usuarios completada.'
            }
            return Response(json.dumps(response_data), content_type='application/json')
        except Exception as e:
            _logger.error(f"Error al cargar datos iniciales: {e}")
            response_data = {
                'status': 'error', 
                'message': str(e)
            }
            return Response(json.dumps(response_data), content_type='application/json')

    @http.route('/session_id', type='http', auth='public', csrf=False)
    def get_session_id(self):
        session_id = request.env.user.id
        response_data ={
            'status' : 'success',
            'session' : session_id,
        }
        return Response(json.dumps(response_data), content_type='application/json')

    @http.route('/api/whatsapp_users', type='http', auth='public', methods=['GET'], csrf=False)
    def get_whatsapp_users(self):
        try:
            users = request.env['whatsapp_message_api.whatsapp_user'].sudo().search([])
            user_data = [
                {
                    'id': user.id, 
                    'name': user.display_name
                } for user in users
            ]
            return json.dumps({'status': 'success', 'users': user_data})
        except Exception as e:
            _logger.error(f"Error obteniendo usuarios: {str(e)}")
            return json.dumps({'status': 'error', 'message': 'Error interno del servidor'})
