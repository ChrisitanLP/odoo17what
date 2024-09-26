import logging
import json
import re
from odoo import http
from odoo.http import request, Response
from datetime import datetime

_logger = logging.getLogger(__name__)

class WhatsappChatController(http.Controller):

    @http.route('/api/chat/initial_load', type='http', auth='public')
    def initial_load(self):
        """Endpoint para iniciar la carga inicial de datos del usuario de WhatsApp."""
        try:
            whatsapp_chat_model = request.env['whatsapp_message_api.whatsapp_chat']
            whatsapp_chat_model.initial_load()
            response_data = {
                'status': 'success', 
                'message': 'Carga inicial de CHATS completada.'
            }
            return Response(json.dumps(response_data), content_type='application/json')
        except Exception as e:
            _logger.error(f"Error al cargar datos iniciales: {e}")
            response_data = {
                'status': 'error', 
                'message': str(e)
            }
            return Response(json.dumps(response_data), content_type='application/json')

    @http.route('/api/chat/process_message', type='json', auth='public', csrf=False)
    def process_message(self):
        """Endpoint para procesar mensajes entrantes desde el WebSocket."""
        try:
            post = request.httprequest.get_json()

            serialized = post.get('from_serialized')
            to_serialized = post.get('to_serialized')
            body = post.get('body')
            timestamp = post.get('timestamp')
            message_type = post.get('messageType')
            user_number = post.get('user_phone_number')
            name_message = post.get('name_message')

            # Determinar si es un grupo o un chat normal
            if '@g.us' in serialized:
                is_group = True
                # Remover '@g.us' de 'from_serialized' si existe
                phone_number = re.sub(r'@g\.us$', '', serialized)
            else:
                is_group = False
                # Remover '@c.us' de 'from_serialized' si existe
                phone_number = re.sub(r'@c\.us$', '', serialized)

            _logger.info("Datos recibidos: %s, %s, %s, %s, %s, %s, %s", serialized, message_type, timestamp, body, user_number, name_message, phone_number)

            if not body:
                body = ""

            if not serialized or not timestamp:
                return {
                    'status': 'error', 
                    'message': 'Faltan parámetros necesarios.'
                }

            user = request.env['whatsapp_message_api.whatsapp_user'].search([('phone_number', '=', user_number)], limit=1)
            user_id = user.id if user else None

            _logger.info ("User id: %s",user_id )

            # Definir el dominio de búsqueda
            domain = [
                ('serialized', '=', serialized),
                ('user_id', '=', user_id),
                ('phone_number', '=', phone_number)
            ]

            # Buscar el chat basado en el número de teléfono
            chat = request.env['whatsapp_message_api.whatsapp_chat'].search(domain, limit=1)
            chat_id = chat.id if chat else None

            _logger.info ("Chat id: %s",chat_id )

            if chat_id:
                # Incrementar el contador de mensajes no leídos
                unread_count = chat.unread_count + 1

                # Actualizar el chat existente
                chat.write({
                    'last_message_body': body,
                    'last_message_type': message_type,
                    'unread_count': unread_count,
                    'timestamp': datetime.utcfromtimestamp(timestamp)
                })
                result =  {
                    'chat_id': chat_id, 
                    'unread_count': unread_count,
                    'name': chat.name,
                    'profile': chat.profile_pic_url,
                    'status_chat': chat.status,
                    'user_attending_id': chat.user_attending_id.id,
                    'user_id' : user_id
                }
            else:
                # Crear un nuevo chat si no existe
                new_chat = request.env['whatsapp_message_api.whatsapp_chat'].create({
                    'serialized': serialized,
                    'phone_number': phone_number,  # Para grupos, esto será el serialized completo
                    'name': name_message,
                    'user_id': user_id,
                    'last_message_body': body,
                    'last_message_type': message_type,
                    'unread_count': 1,
                    'timestamp': datetime.utcfromtimestamp(timestamp),
                    'status': 'pendiente',
                    'is_group': is_group
                })
                result =  {
                    'chat_id': new_chat.id, 
                    'unread_count': new_chat.unread_count,
                    'name': name_message,
                    'profile': new_chat.profile_pic_url,
                    'status_chat': new_chat.status,
                    'user_attending_id': new_chat.user_attending_id.id,
                    'user_id' : user_id
                }

            return {
                'status': 'success',
                'message': 'Mensaje procesado correctamente.',
                **result  
            }

        except Exception as e:
            _logger.error(f"Error al procesar el mensaje: {e}")
            return {'status': 'error', 'message': str(e)}

    @http.route('/api/chat/update_status', type='json', auth='public', csrf=False)
    def update_chat_status(self):
        try:
            post = request.httprequest.get_json()

            chat_id = post.get('chat_id')
            status_chat = post.get('status_chat')

            if not chat_id or not status_chat:
                response = {
                    'status': 'error', 
                    'message': 'Faltan parámetros necesarios'
                }
                _logger.info(f'Returning response: {json.dumps(response)}')
                return response

            chat = request.env['whatsapp_message_api.whatsapp_chat'].browse(int(chat_id))
            user_id = request.env.user.id

            if chat.exists():
                if status_chat == 'atendiendo':
                    # Verifica si el chat ya está siendo atendido por otro usuario
                    if chat.user_attending_id and chat.user_attending_id.id != user_id:
                        return {
                            'status': 'error', 
                            'message': 'Este chat ya está siendo atendido por otro usuario.'
                        }

                    # Actualiza el estado del chat y asigna el usuario que lo está atendiendo
                    chat.write({
                        'status': status_chat,
                        'user_attending_id': user_id
                    })
                elif status_chat == 'pendiente':
                    # Desasigna el usuario y actualiza el estado a pendiente
                    chat.write({
                        'status': status_chat,
                        'user_attending_id': False
                    })
                elif status_chat == 'atendido':
                    # Establece unread_count a 0 y desasigna el usuario cuando el estado es 'atendido'
                    chat.write({
                        'status': status_chat,
                        'unread_count': 0,
                        'user_attending_id': False
                    })
                    
                last_message_body = chat.last_message_body
                last_message_type = chat.last_message_type
                unread_count = chat.unread_count

                return {
                    'status': 'success', 
                    'message': 'Estado del chat actualizado.', 
                    'last_message_body': last_message_body, 
                    'unread_count': unread_count, 
                    'last_message_type': last_message_type
                }
            else:
                return {
                    'status': 'error', 
                    'message': 'Chat no encontrado.'
                }
        except Exception as e:
            _logger.error(f"Error al actualizar el estado del chat: {e}")
            return {
                'status': 'error', 
                'message': str(e)
            }

    @http.route('/api/whatsapp', auth='public', website=True)
    def list_combined_chats_contacts(self, **kwargs):
        """Endpoint para mostrar la plantilla inicial con chats y contactos de WhatsApp."""
        try:
            # Llamadas a los métodos de carga inicial (si es necesario)
            self.load_initial_data()

            current_user_id = request.env.user.id

            # Obtener chats ordenados por timestamp
            chats = request.env['whatsapp_message_api.whatsapp_chat'].search(
                 [
                    '|',
                    ('unread_count', '>', 0),
                    ('user_attending_id', '=', current_user_id),
                    ('status', '!=', 'atendido')
                ],
                order='timestamp desc'  # Ordenar los chats por timestamp en orden descendente
            )
            contacts = request.env['whatsapp_message_api.whatsapp_contact'].search([], order='name asc')

            # Renderizar la plantilla principal que contiene el contenedor para las plantillas dinámicas
            return request.render('whatsapp_message_api.chats_and_contacts_template', {
                'chats': chats,
                'contacts': contacts
            })
        except Exception as e:
            _logger.error(f"Error al cargar datos combinados de chats y contactos: {e}")
            return request.render('whatsapp_message_api.error_template', {'error_message': str(e)})

    @http.route('/api/whatsapp/<template_name>', auth='public', website=True)
    def get_template(self, template_name, **kwargs):
        """Endpoint para cargar una plantilla específica."""
        try:
            # Datos para cada plantilla
            data = {}
            if template_name == 'contacts_template':
                contacts = request.env['whatsapp_message_api.whatsapp_contact'].search([], order='name asc')
                data = {'contacts': contacts}
            elif template_name == 'products_template':
                products = request.env['product.template'].search([])
                data = {'products': products}
            elif template_name == 'default_messages_template':
                messages = request.env['whatsapp_message_api.default_message'].search([])
                data = {'messages': messages}
            else:
                return request.render('http_routing.404')

            # Renderizar la plantilla con los datos
            return request.render(f'whatsapp_message_api.{template_name}', data)
        except Exception as e:
            _logger.error(f"Error al cargar la plantilla {template_name}: {e}")
            return request.render('http_routing.404')
    
    def load_initial_data(self):
        """Método para cargar datos iniciales de usuarios, chats, mensajes por defecto y stickers."""
        try:
            # Cargar datos de usuarios
            whatsapp_user_model = request.env['whatsapp_message_api.whatsapp_user']
            whatsapp_user_model.initial_load()
            _logger.info('Carga inicial de Usuarios completada.')

            # Cargar datos de chats
            whatsapp_chat_model = request.env['whatsapp_message_api.whatsapp_chat']
            whatsapp_chat_model.initial_load()
            _logger.info('Carga inicial de CHATS completada.')

            # Cargar datos de contactos
            whatsapp_contact_model = request.env['whatsapp_message_api.whatsapp_contact']
            whatsapp_contact_model.initial_load()
            _logger.info('Carga inicial de Contactos completada.')

            # Crear mensajes por defecto
            default_message_model = request.env['whatsapp_message_api.default_message']
            default_message_model.create_default_messages()
            _logger.info('Mensajes por defecto generados.')

            # Crear stickers por defecto
            sticker_model = request.env['whatsapp_message_api.whatsapp_sticker']
            sticker_model.create_default_stickers()
            _logger.info('Stickers por defecto creados exitosamente.')

        except Exception as e:
            _logger.error(f"Error al cargar datos iniciales: {e}")
            raise e