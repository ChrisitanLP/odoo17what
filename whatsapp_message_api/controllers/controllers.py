import json
import logging
import requests
from odoo import http
from odoo.http import request, Response
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class WhatsappMessageApi(http.Controller):

    def _get_api_url(self):
        try:
            api_url = request.env['ir.config_parameter'].sudo().get_param('api_base')
            if not api_url:
                raise UserError("La URL de la API no está configurada en los parámetros del sistema.")
            return api_url
        except Exception as e:
            _logger.error(f"Error al obtener la URL de la API: {e}")
            raise UserError("No se pudo obtener la URL de la API. Por favor, verifica la configuración del sistema.")
    
    @http.route('/whatsapp/connections', auth='public', type='http', website=True)
    def list_connections(self, **kwargs):
        """Endpoint para listar todas las conexiones de WhatsApp."""
        try:
            user = request.env.user
            
            # Verifica si el usuario pertenece al grupo de administradores
            if not user.has_group('base.group_system'):
                return request.render('whatsapp_message_api.custom_landing_page')  # Redirige a una página de error de acceso no autorizado

            # Obtener todas las conexiones
            connections = request.env['whatsapp_message_api.whatsapp_connection'].search([])
            
            # Renderizar la plantilla con las conexiones
            return request.render('whatsapp_message_api.whatsapp_autentication', {
                'connections': connections
            })
        except Exception as e:
            _logger.error(f"Error al cargar conexiones de WhatsApp: {e}")
            return request.render('http_routing.404')

    @http.route('/api/connection/add', type='http', auth='public', csrf=False)
    def add_connection(self, **kwargs):
        try:
            # Verifica los datos recibidos
            _logger.info("Datos recibidos: %s", kwargs)

            # Obtener parámetros del JSON
            name = kwargs.get('name')
            phone_number = kwargs.get('phone_number')
            color = kwargs.get('color')

            # Verificar parámetros requeridos
            if not phone_number:
                _logger.error("Phone number is required but not provided.")
                return Response(json.dumps({'error': "Debe proporcionar un número de teléfono."}), content_type='application/json', status=400)

            # Llamar al método del modelo para agregar la conexión
            connection = request.env['whatsapp_message_api.whatsapp_connection'].add_connection(name, phone_number, color)

            # Obtener la URL base de la API
            api_base_url = self._get_api_url()

            # Enviar el mensaje (puedes usar tu lógica existente para enviar mensajes)
            data = {
                'number': phone_number,
            }
            response = requests.post(f"{api_base_url}/addClient", json=data)

            # Verificar respuesta de la solicitud
            if response.status_code != 200:
                _logger.error("Failed to send message. Status code: %s", response.status_code)
                return Response(json.dumps({'error': 'Failed to send message.'}), content_type='application/json', status=500)

            # Respuesta exitosa
            return Response(json.dumps({
                'success': True,
                'connection': {
                    'id': connection.id,
                    'name': name,
                    'phone_number': phone_number,
                    'color': color
                }
            }), content_type='application/json')
        except UserError as ue:
            _logger.error("Error en el controlador: %s", str(ue))
            return Response(json.dumps({'success': False, 'message': str(ue)}), content_type='application/json', status=400)
        except Exception as e:
            _logger.error("Error en el controlador: %s", str(e))
            return Response(json.dumps({'success': False, 'message': str(e)}), content_type='application/json', status=500)

    @http.route('/api/connection/delete/<int:connection_id>', type='http', auth='public', methods=['POST'], csrf=False)
    def delete_connection(self, connection_id):
        try:
            # Llamar al método del modelo para eliminar la conexión
            connection_model = request.env['whatsapp_message_api.whatsapp_connection']

            # Buscar la conexión por ID y obtener el número de teléfono
            connection = connection_model.sudo().search([('id', '=', connection_id)], limit=1)
            if not connection:
                _logger.error(f"Conexión con ID {connection_id} no encontrada.")
                return Response(json.dumps({'status': 'error', 'message': 'Conexión no encontrada.'}), content_type='application/json', status=404)
            
            phone_number = connection.phone_number

             # Llamar a la API externa para eliminar el cliente
            api_base_url = self._get_api_url()  # Usa el método adecuado para obtener la URL base de la API
            data = {'number': phone_number}
            response = requests.post(f"{api_base_url}/removeClient", json=data)

            # Verificar la respuesta de la API
            if response.status_code != 200:
                _logger.error(f"Error al eliminar cliente en la API externa. Status code: {response.status_code}")
                return Response(json.dumps({'status': 'error', 'message': 'Error al eliminar en la API externa.'}), content_type='application/json', status=500)

            connection_model.delete_connection(connection_id)

            _logger.info(f"Conexión con ID {connection_id} eliminada correctamente.")
            return Response(json.dumps({'status': 'success'}), content_type='application/json')

        except UserError as ue:
            _logger.error(f"Error al eliminar la conexión: {ue}")
            return Response(json.dumps({'status': 'error', 'message': str(ue)}), content_type='application/json', status=400)

        except Exception as e:
            _logger.error(f"Ocurrió un error al eliminar la conexión: {e}")
            return Response(json.dumps({'status': 'error', 'message': 'Ocurrió un error inesperado.'}), content_type='application/json', status=500)

    @http.route('/api/chat/id', type='json', auth='public', methods=['POST'], csrf=False)
    def get_chat_id(self):
        try:
            post = request.httprequest.get_json()
            serialized = post.get('serialized')
            user_id = post.get('user_id')
            phone_number = post.get('phone_number')

            # Validar parámetros
            if not serialized and not user_id and not phone_number:
                _logger.warning('No parameters provided for chat ID retrieval.')
                response = {'status': 'error', 'message': 'No parameters provided'}
                _logger.info(f'Returning response: {json.dumps(response)}')
                return response

            # Buscar chat basado en todos los parámetros
            domain = [
                ('serialized', '=', serialized),
                ('user_id', '=', user_id),
                ('phone_number', '=', phone_number)
            ]

            chat = request.env['whatsapp_message_api.whatsapp_chat'].search(domain, limit=1)
            chat_id = chat.id if chat else None

            contact = request.env['whatsapp_message_api.whatsapp_contact'].search(domain, limit=1)
            contact_id = contact.id if contact else None

            if chat_id:
                response = {
                    'status': 'success', 
                    'chat_id': chat_id,
                    'contact_id': contact_id
                }
                _logger.info(f'Chat found: {chat_id}')
            else:
                response = {
                    'status': 'error', 
                    'message': 'Chat not found'
                }
                _logger.warning('Chat not found with provided parameters.')

            _logger.info(f'Returning response: {json.dumps(response)}')
            return response

        except Exception as e:
            _logger.exception('An error occurred while retrieving the chat ID.')
            response = {
                'status': 'error', 
                'message': str(e)
            }
            _logger.info(f'Returning response: {json.dumps(response)}')
            return response

    @http.route('/menu_opciones', auth='public', website=True)
    def show_custom_landing_page(self, **kwargs):
        """Muestra la página de inicio personalizada con dos secciones."""
        return request.render('whatsapp_message_api.custom_landing_page')