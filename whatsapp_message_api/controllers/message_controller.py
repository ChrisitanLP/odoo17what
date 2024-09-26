import logging
import os
import base64
import requests
import json
from odoo import http
from odoo.http import request, Response, route
from urllib.parse import urlparse
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class WhatsappMessageController(http.Controller):

    def _get_api_url(self):
        try:
            api_url = request.env['ir.config_parameter'].sudo().get_param('api_base')
            if not api_url:
                raise UserError("La URL de la API no está configurada en los parámetros del sistema.")
            return api_url
        except Exception as e:
            _logger.error(f"Error al obtener la URL de la API: {e}")
            raise UserError("No se pudo obtener la URL de la API. Por favor, verifica la configuración del sistema.")

    @http.route('/api/message/initial_load', type='http', auth='public', csrf=False)
    def initial_load(self, chat_id):
        """Endpoint para iniciar la carga inicial de datos del usuario de WhatsApp."""
        try:
            whatsapp_message_model = request.env['whatsapp_message_api.whatsapp_message']
            whatsapp_message_model.initial_load(chat_id)
            response_data = {
                'status': 'success', 
                'message': 'Carga inicial de Mensajes completada.'
            }
            return Response(json.dumps(response_data), content_type='application/json')
        except Exception as e:
            _logger.error(f"Error al cargar datos iniciales: {e}")
            response_data = {
                'status': 'error', 
                'message': str(e)
            }
            return Response(json.dumps(response_data), content_type='application/json')

    @http.route('/api/messages/<int:chat_id>', type='http', auth='public', csrf=False)
    def get_messages(self, chat_id):
        """Obtiene los mensajes para un chat específico."""
        try:
            whatsapp_message_model = request.env['whatsapp_message_api.whatsapp_message']
            whatsapp_message_model.initial_load(chat_id)
            _logger.info('Carga inicial de mensajes completada.')

            # Obtener el chat
            chat = request.env['whatsapp_message_api.whatsapp_chat'].browse(chat_id)
            group_id = chat.group_id.id
            is_group = chat.is_group

            member_names = {}
        
            # Verificar si es un chat grupal
            if is_group:
                # Obtener los miembros del grupo y sus números de teléfono
                group_members = request.env['whatsapp_message_api.whatsapp_group_member'].search([('group_id', '=', group_id)])
                member_names = {member.id: member.phone_number for member in group_members}
                _logger.info(member_names)
            
            # Obtener los mensajes
            messages = request.env['whatsapp_message_api.whatsapp_message'].search([('chat_id', '=', chat_id)])

            response_data = {
                'status': 'success',
                'chat': {
                    'name': chat.name,
                    'profile_pic_url': chat.profile_pic_url,
                    'status': chat.status,
                    'assigned_user_id': chat.user_attending_id.id,
                    'user_id': chat.user_id.id,
                    'is_group' : is_group,
                    'member_phones' : member_names
                },
                'messages': [{
                            'id' : msg.id,
                            'from_user': msg.from_user,
                            'serialized': msg.serialized,
                            'body': msg.body,
                            'type': msg.media_type,
                            'from_Me': msg.from_Me,
                            'timestamp': msg.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                            'media_data': msg.media_base64,
                            'media_temp_url': msg.media_temp_url,
                            'hasQuotedMsg': msg.hasQuotedMsg,
                            'quoted_id': msg.quoted_serialized,
                            'quoted_body' : msg.quoted_body,
                            'quoted_from_user': msg.quoted_from_user,
                            'quoted_to_user': msg.quoted_to_user,
                            'quoted_type': msg.quoted_type,
                            'latitude': msg.location_latitude,
                            'longitude': msg.location_longitude,
                            'media_mime_type': msg.mime_type} 
                            for msg in messages]
            }
            return Response(json.dumps(response_data), content_type='application/json')
        except Exception as e:
            _logger.error(f"Error al obtener mensajes: {e}")
            chat = request.env['whatsapp_message_api.whatsapp_chat'].browse(chat_id)
            response_data = {
                'status': 'error',
                'message': str(e),
                'chat_info': {  # Cambia 'chat' a 'chat_info'
                    'name': chat.name,
                    'id': chat.id,
                    'profile_pic_url': chat.profile_pic_url,
                    'status': chat.status,
                    'assigned_user_id': chat.user_attending_id.id,
                },
                'messages': []
            }
            return Response(json.dumps(response_data), content_type='application/json')

    @http.route('/api/group_messages/<int:chat_id>', type='http', auth='public', csrf=False)
    def get_messages_group(self, chat_id):
        """Obtiene los mensajes para un chat específico."""
        try:
            whatsapp_message_model = request.env['whatsapp_message_api.whatsapp_message']
            whatsapp_message_model.initial_load(chat_id)
            _logger.info('Carga inicial de mensajes completada.')

            # Obtener el chat
            chat = request.env['whatsapp_message_api.whatsapp_chat'].browse(chat_id)
            group_id = chat.group_id.id

            # Obtener los mensajes
            messages = request.env['whatsapp_message_api.whatsapp_message'].search([('chat_id', '=', chat_id)])
            
            # Obtener los miembros del grupo y sus nombres
            group_members = request.env['whatsapp_message_api.whatsapp_group_member'].search([('group_id', '=', group_id)])
            member_names = {member.id: member.phone_number for member in group_members}

            response_data = {
                'status': 'success',
                'chat': {
                    'name': chat.name,
                    'profile_pic_url': chat.profile_pic_url
                },
                'messages': [{'from_user': msg.from_user,
                            'body': msg.body,
                            'type': msg.media_type,
                            'from_Me': msg.from_Me,
                            'timestamp': msg.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                            'media_data': msg.media_base64,  # Incluye media_base64
                            'media_mime_type': msg.mime_type,
                            'member_name': member_names.get(msg.from_user, 'Desconocido')} 
                            for msg in messages]
            }
            return Response(json.dumps(response_data), content_type='application/json')
        except Exception as e:
            _logger.error(f"Error al obtener mensajes: {e}")
            response_data = {
                'status': 'error', 
                'message': str(e)
            }
            return Response(json.dumps(response_data), content_type='application/json')

    @http.route('/api/message/send-sticker', type='http', auth='public', methods=['POST'], csrf=False)
    def send_message_sticker(self):
        """Endpoint para enviar un mensaje."""
        try:
            post = request.httprequest.get_json()
            chat_id = post.get('chat_id')
            sticker_url = post.get('sticker_url')
            sticker_name = post.get('file_name')

            if not chat_id or not sticker_url:
                response_data = {
                    'status': 'error', 
                    'message': 'Faltan parámetros requeridos.'
                }
                return Response(json.dumps(response_data), content_type='application/json')

            # Obtener el número de teléfono asociado con el chat_id
            chat = request.env['whatsapp_message_api.whatsapp_chat'].search([('id', '=', chat_id)], limit=1)
            if not chat:
                response_data = {
                    'status': 'error', 
                    'message': 'Chat no encontrado.'
                }
                return Response(json.dumps(response_data), content_type='application/json')

            phone_number = chat.phone_number
            group_number = chat.group_id.group_number
            clientId = chat.user_id.connection_id.phone_number
            isGroup = chat.is_group

            # Verificar si la URL es una URL de localhost y convertirla a ruta de sistema de archivos
            if sticker_url.startswith('http://') or sticker_url.startswith('https://'):
                parsed_url = urlparse(sticker_url)

                # Reemplazar el prefijo 'http://localhost' por la ruta absoluta del sistema de archivos
                current_dir = os.path.dirname(os.path.abspath(__file__))
                local_file_path = os.path.join(current_dir, '..', parsed_url.path.lstrip('/'))

                # Convertir las barras invertidas a barras diagonales
                local_file_path = local_file_path.replace('\\', '/').replace('//', '/')
                _logger.info(local_file_path)

                # Encuentra la posición de 'controllers/' en la ruta original
                controllers_index = local_file_path.find('controllers/')
        
                # Extrae la parte base de la ruta
                if controllers_index != -1:
                    base_dir = local_file_path[:controllers_index]
                else:
                    base_dir = local_file_path

                new_relative_path = 'static/src/img/stickers/'+ sticker_name

                adjusted_path = os.path.join(base_dir, new_relative_path)
                adjusted_path = os.path.normpath(adjusted_path)

                sticker_url = adjusted_path
                _logger.info(sticker_url)
            
            api_base_url = self._get_api_url()

            if(isGroup):
                # Obtener la URL base de la API
                api_url = f"{api_base_url}/sendSticker"  
                data = {
                    'tel': group_number,
                    'stickerPath': sticker_url,
                    'clientId': clientId,
                    'isGroup': isGroup,
                }
            else:
                # Obtener la URL base de la API
                api_url = f"{api_base_url}/sendSticker"  
                data = {
                    'tel': phone_number,
                    'stickerPath': sticker_url,
                    'clientId': clientId,
                    'isGroup': isGroup,
                }

            # Realiza la solicitud POST a la API externa
            response = requests.post(api_url, json=data)

            if response.status_code == 200:
                response_data = response.json()
                if response_data.get('success'):
                    response_data = {
                        'status': 'success', 
                        'message': 'Mensaje enviado correctamente.'
                    }
                    return Response(json.dumps(response_data), content_type='application/json')
                else:
                    response_data = {
                        'status': 'error', 
                        'message': response_data.get('message')
                    }
                    return Response(json.dumps(response_data), content_type='application/json')
            else:
                response_data = {
                    'status': 'error', 
                    'message': 'Error en la respuesta de la API externa.'
                }
                return Response(json.dumps(response_data), content_type='application/json')
        except Exception as e:
            _logger.error(f"Error al enviar mensaje: {e}")
            response_data = {
                'status': 'error', 
                'message': str(e)
            }
            return Response(json.dumps(response_data), content_type='application/json')


    @http.route('/api/message/send', type='http', auth='public', methods=['POST'], csrf=False)
    def send_message(self):
        """Endpoint para enviar un mensaje."""
        try:
            post = request.httprequest.get_json()
            if not post:
                response_data = {
                    'status': 'error', 
                    'message': 'No se proporcionaron datos en el cuerpo de la solicitud.'
                }
                return Response(json.dumps(response_data), content_type='application/json', status=400)
            
            chat_id = post.get('chat_id')
            message_body = post.get('message_body')

            if not chat_id or not message_body:
                response_data = {
                    'status': 'error', 
                    'message': 'Faltan parámetros requeridos.'
                }
                return Response(json.dumps(response_data), content_type='application/json')

            # Obtener el número de teléfono asociado con el chat_id
            chat = request.env['whatsapp_message_api.whatsapp_chat'].search([('id', '=', chat_id)], limit=1)
            if not chat:
                response_data = {
                    'status': 'error', 
                    'message': 'Chat no encontrado.'
                }
                return Response(json.dumps(response_data), content_type='application/json')

            isGroup = chat.is_group
            phone_number = chat.phone_number
            groupNumber = chat.group_id.group_number
            clientId = chat.user_id.connection_id.phone_number

            # Obtener la URL base de la API
            api_base_url = self._get_api_url()

            if isGroup:
                api_url = f"{api_base_url}/sendGroupMessage"  # Cambia esto a tu URL de API real
                data = {
                    'clientId': clientId,
                    'groupId': groupNumber,
                    'mensaje': message_body,
                }
            else:
                api_url = f"{api_base_url}/sendMessage"  # Cambia esto a tu URL de API real
                data = {
                    'clientId': clientId,
                    'tel': phone_number,
                    'mensaje': message_body,
                }

            # Realiza la solicitud POST a la API externa
            response = requests.post(api_url, json=data)

            if response.status_code == 200:
                response_data = response.json()
                if response_data.get('success'):
                    response_data = {
                        'status': 'success', 
                        'message': 'Mensaje enviado correctamente.'
                    }
                    return Response(json.dumps(response_data), content_type='application/json')
                else:
                    response_data = {
                        'status': 'error', 
                        'message': response_data.get('message')
                    }
                    return Response(json.dumps(response_data), content_type='application/json')
            else:
                _logger.error(f"Error en la respuesta de la API externa: {response.text}")
                response_data = {
                    'status': 'error', 
                    'message': 'Error en la respuesta de la API externa.'
                }
                return Response(json.dumps(response_data), content_type='application/json')
        except Exception as e:
            _logger.error(f"Error al enviar mensaje: {e}")
            response_data = {
                'status': 'error', 
                'message': str(e)
            }
            return Response(json.dumps(response_data), content_type='application/json')

    @http.route('/api/message/send-default-messages', type='http', auth='public', methods=['POST'], csrf=False)
    def send_default_message(self):
        """Endpoint para enviar un mensaje."""
        try:
            post = request.httprequest.get_json()
            chat_id = post.get('chat_id')
            default_id = post.get('default_id')

            if not chat_id or not default_id:
                response_data = {
                    'status': 'error', 
                    'message': 'Faltan parámetros requeridos.'
                }
                return Response(json.dumps(response_data), content_type='application/json')

            # Obtener el número de teléfono asociado con el chat_id
            chat = request.env['whatsapp_message_api.whatsapp_chat'].search([('id', '=', chat_id)], limit=1)
            if not chat:
                response_data = {
                    'status': 'error', 
                    'message': 'Chat no encontrado.'
                }
                return Response(json.dumps(response_data), content_type='application/json')

            phone_number = chat.phone_number
            group_number = chat.group_id.group_number
            clientId = chat.user_id.connection_id.phone_number

            # Obtener el número de teléfono asociado con el chat_id
            default = request.env['whatsapp_message_api.default_message'].search([('id', '=', default_id)], limit=1)
            if not default:
                response_data = {
                    'status': 'error', 
                    'message': 'Mensaje por defecto no encontrado.'
                }
                return Response(json.dumps(response_data), content_type='application/json')

            type_default = default.type
            file_name = default.file_name
            message_body = ""
            file_url = default.file_url if default.type in ['document', 'image'] else None

            # Generar el cuerpo del mensaje según el tipo
            if type_default == 'text':
                message_body = f"*{default.text}*"
            elif type_default == 'location':
                message_body = f"https://www.google.com/maps?q={default.location_latitude},{default.location_longitude}"
            elif type_default == 'document':
                message_body = f"{default.file_url}"
            elif type_default == 'image':
                message_body = f"{default.file_url}"
            elif type_default == 'web_page':
                message_body = f"{default.web_url}"
            else:
                response_data = {'status': 'error', 'message': 'Tipo de mensaje no soportado.'}
                return Response(json.dumps(response_data), content_type='application/json')

            # Verificar si la URL es una URL de localhost y convertirla a ruta de sistema de archivos
            if file_url:
                parsed_url = urlparse(file_url)

                # Reemplazar el prefijo 'http://localhost' por la ruta absoluta del sistema de archivos
                current_dir = os.path.dirname(os.path.abspath(__file__))
                local_file_path = os.path.join(current_dir, '..', parsed_url.path.lstrip('/'))

                # Convertir las barras invertidas a barras diagonales
                local_file_path = local_file_path.replace('\\', '/').replace('//', '/')
                _logger.info(local_file_path)

                # Encuentra la posición de 'controllers/' en la ruta original
                controllers_index = local_file_path.find('controllers/')

                # Extrae la parte base de la ruta
                if controllers_index != -1:
                    base_dir = local_file_path[:controllers_index]
                else:
                    base_dir = local_file_path

                new_relative_path = 'static/src/files/' + file_name
                adjusted_path = os.path.join(base_dir, new_relative_path)
                adjusted_path = os.path.normpath(adjusted_path)

                file_path = adjusted_path
                _logger.info(file_url)

            # Obtener la URL base de la API
            api_base_url = self._get_api_url()
            isGroup = chat.is_group

            if file_url:
                if isGroup:
                    api_url = f"{api_base_url}/sendImage"  # Cambia esto a tu URL de API real para enviar archivos a grupos
                    data = {
                        'tel': group_number,
                        'imagePath': file_path,
                        'clientId': clientId,
                        'isGroup': isGroup,
                    }
                else:
                    api_url = f"{api_base_url}/sendImage"  # Cambia esto a tu URL de API real para enviar archivos
                    data = {
                        'tel': phone_number,
                        'imagePath': file_path,
                        'clientId': clientId,
                        'isGroup' : isGroup,
                    }
            else:
                if isGroup:
                    api_url = f"{api_base_url}/sendGroupMessage"  # Cambia esto a tu URL de API real
                    data = {
                        'groupId': group_number,
                        'mensaje': message_body,
                        'clientId': clientId,
                    }
                else:
                    api_url = f"{api_base_url}/sendMessage"  # Cambia esto a tu URL de API real
                    data = {
                        'tel': phone_number,
                        'mensaje': message_body,
                        'clientId': clientId,
                    }

            response = requests.post(api_url, json=data)

            if response.status_code == 200:
                response_data = response.json()
                if response_data.get('success'):
                    response_data = {
                        'status': 'success', 
                        'message': 'Mensaje enviado correctamente.'
                    }
                else:
                    response_data = {
                        'status': 'error', 
                        'message': response_data.get('message')
                    }
            else:
                response_data = {
                    'status': 'error', 
                    'message': 'Error en la respuesta de la API externa.'
                }

            return Response(json.dumps(response_data), content_type='application/json')
        except Exception as e:
            _logger.error(f"Error al enviar mensaje: {e}")
            response_data = {
                'status': 'error', 
                'message': str(e)
            }
            return Response(json.dumps(response_data), content_type='application/json')

    def convert_image_url_to_base64(image_url):
        try:
            # Descargar la imagen
            response = requests.get(image_url)
            response.raise_for_status()  # Verificar que la solicitud fue exitosa

            # Obtener el tipo de contenido (Content-Type) para determinar el prefijo base64
            content_type = response.headers.get('Content-Type', '')
            
            # Obtener los datos binarios de la imagen
            image_binary = response.content

            # Convertir a base64
            image_base64 = base64.b64encode(image_binary).decode('utf-8')

            # Determinar el prefijo según el tipo de imagen
            if 'image/png' in content_type:
                image_base64 = f"data:image/png;base64,{image_base64}"
            elif 'image/jpeg' in content_type:
                image_base64 = f"data:image/jpeg;base64,{image_base64}"
            else:
                image_base64 = f"data:image/octet-stream;base64,{image_base64}"

            return image_base64

        except Exception as e:
            _logger.error(f"Error al convertir la URL de la imagen a base64: {e}")
            return None

    @http.route('/api/message/send-product', type='json', auth='public', methods=['POST'], csrf=False)
    def send_product(self):
        """Endpoint para enviar un producto como mensaje en un chat específico."""
        try:
            post = request.httprequest.get_json()
            chat_id = post.get('chat_id')
            product_id = post.get('product_id')

            if not chat_id or not product_id:
                response_data = {
                    'status': 'error', 
                    'message': 'Faltan parámetros requeridos.'
                }
                return Response(json.dumps(response_data), content_type='application/json')

            # Obtener el chat asociado con el chat_id
            chat = request.env['whatsapp_message_api.whatsapp_chat'].search([('id', '=', chat_id)], limit=1)
            if not chat:
                response_data = {
                    'status': 'error', 
                    'message': 'Chat no encontrado.'
                }
                return Response(json.dumps(response_data), content_type='application/json')

            phone_number = chat.phone_number
            clientId = chat.user_id.connection_id.phone_number
            isGroup = chat.is_group
            group_number = chat.group_id.group_number if isGroup else None

            # Obtener el producto
            product = request.env['product.template'].browse(product_id)
            if not product:
                response_data = {
                    'status': 'error', 
                    'message': 'Producto no encontrado.'
                }
                return Response(json.dumps(response_data), content_type='application/json')

            # Preparar el mensaje
            message_body = f"*Producto:* {product.name}\n*Precio:* ${product.list_price}"
            base_url = request.httprequest.host_url  # Obtiene la URL base del servidor
            image_url = f"{base_url}web/image/product.template/{product.id}/image_1920"

            _logger.info(f"URL de la imagen: {image_url}")

            # Obtener la imagen desde el campo binario de Odoo
            image_binary = product.image_1920

            _logger.info(f"Contenido del binario de la imagen: {image_binary}")
            
            if image_binary:
                # Convertir la imagen binaria en una cadena de texto
                image_text = image_binary.decode('utf-8')  # Decodifica bytes a texto
            else:
                image_text = None

            _logger.info(f"Cadena de texto de imagen: {image_text}")

            image_base64 = f"data:image/png;base64,{image_text}"

            # Enviar el mensaje (puedes usar tu lógica existente para enviar mensajes)
            api_base_url = self._get_api_url()

            if isGroup:
                api_url = f"{api_base_url}/sendGroupProducts"
                data = {
                    'groupId': group_number,
                    'mensaje': message_body,
                    'imagen': image_base64,  # Enviar imagen en base64 para grupos
                    'clientId': clientId
                }
            else:
                api_url = f"{api_base_url}/sendMessageProducts"
                data = {
                    'tel': phone_number,
                    'mensaje': message_body,
                    'imagen': image_base64,  # Enviar imagen en base64 para usuarios individuales
                    'clientId': clientId
                }

            response = requests.post(api_url, json=data)

            if response.status_code == 200:
                response_data = response.json()
                if response_data.get('success'):
                    return {
                        'status': 'success', 
                        'message': 'Producto enviado correctamente.'
                    }
                else:
                    return {
                        'status': 'error', 
                        'message': response_data.get('message')
                    }
            else:
                return {
                    'status': 'error', 
                    'message': 'Error en la respuesta de la API externa.'
                }

        except Exception as e:
            _logger.error(f"Error al enviar producto: {e}")
            return {
                'status': 'error', 
                'message': str(e)
            }

    @http.route('/send_file_path', type='json', auth='user', methods=['POST'])
    def send_file_path(self):
        post = request.httprequest.get_json()
        file_name = post.get('file_name')
        file_content = post.get('file_content')
        chat_id = post.get('chatId')
        message_body = post.get('messageBody')

        _logger.info(f"file_name: {file_name}")
        _logger.info(f"file_content: {file_content}")
        _logger.info(f"Message body;  {message_body}")

        if not file_name or not file_content:
            return {
                'status': 'error', 
                'message': 'Faltan datos del archivo'
            }
    
        chat = request.env['whatsapp_message_api.whatsapp_chat'].search([('id', '=', chat_id)], limit=1)
        if not chat:
            return {
                'status': 'error', 
                'message': 'Chat no encontrado.'
            }
                
        phone_number = chat.phone_number
        clientId = chat.user_id.connection_id.phone_number
        isGroup = chat.is_group
        _logger.info(f"Chat numero: {phone_number}")
        _logger.info(f"Cliente:  {clientId}")

        # Crear el JSON para enviar a la API
        data = {
            'clientId': clientId,
            'message': message_body,
            'fileName': file_name,
            'fileContent': file_content,
            'chatId': phone_number,
            'isGroup': isGroup
        }

        # URL de la API en Node.js
        api_base_url = self._get_api_url()
        api_url = f"{api_base_url}/sendMessageOrFile2"  # Asegúrate de que la URL es correcta

        try:
            response = requests.post(api_url, json=data)
            response.raise_for_status()  # Lanza un error para códigos de estado HTTP no exitosos
            response_data = response.json()
            return {
                'status': 'success',
                'data': response_data
            }
        except requests.exceptions.RequestException as e:
            return {
                'status': 'error', 
                'message': str(e)
            }

    @http.route('/api/message/send-file', type='http', auth='public', methods=['POST'], csrf=False)
    def send_message_file(self):
        """Endpoint para enviar un mensaje con archivo."""
        try:
            # Acceder a los archivos enviados
            uploaded_file = request.httprequest.files.get('file')
            chat_id = request.params.get('chat_id')
            message_body = request.params.get('message_body')

            _logger.info(f"Recibido chat_id: {chat_id}, archivo: {uploaded_file}, message_body: {message_body}")

            if not chat_id or not uploaded_file or not message_body:
                response_data = {
                    'status': 'error', 
                    'message': 'Faltan parámetros requeridos.'
                }
                return Response(json.dumps(response_data), content_type='application/json')

            chat = request.env['whatsapp_message_api.whatsapp_chat'].search([('id', '=', chat_id)], limit=1)
            if not chat:
                response_data = {
                    'status': 'error', 
                    'message': 'Chat no encontrado.'
                }
                return Response(json.dumps(response_data), content_type='application/json')

            phone_number = chat.phone_number

            api_base_url = self._get_api_url()
            api_url = f"{api_base_url}/sendMessageFiles"
            data = {
                'tel': phone_number,
                'archivo': uploaded_file,
                'mensaje': message_body
            }

            response = requests.post(api_url, json=data)
            if response.status_code == 200:
                response_data = response.json()
                if response_data.get('success'):
                    response_data = {
                        'status': 'success', 
                        'message': 'Mensaje enviado correctamente.'
                    }
                    return Response(json.dumps(response_data), content_type='application/json')
                else:
                    response_data = {
                        'status': 'error', 
                        'message': response_data.get('message', 'Error desconocido en la respuesta de la API externa.')
                    }
                    return Response(json.dumps(response_data), content_type='application/json')
            else:
                response_data = {
                    'status': 'error', 
                    'message': 'Error en la respuesta de la API externa.'
                }
                return Response(json.dumps(response_data), content_type='application/json')
        except Exception as e:
            _logger.error(f"Error al enviar mensaje: {e}", exc_info=True)
            response_data = {
                'status': 'error', 
                'message': 'Ha ocurrido un error al procesar la solicitud.'
            }
            return Response(json.dumps(response_data), content_type='application/json')


    @route('/api/message/forward', type='http', auth='public', methods=['POST'], csrf=False)
    def forward_message(self):
        try:
            post = request.httprequest.get_json()
            if not post:
                response_data = {
                    'status': 'error', 
                    'message': 'No se proporcionaron datos en el cuerpo de la solicitud.'
                }
                return Response(json.dumps(response_data), content_type='application/json', status=400)

            message_id = post.get('message_id')
            to_chat_id = post.get('to_chat_id')

            if not message_id or not to_chat_id:
                response_data = {
                    'status': 'error', 
                    'message': 'Faltan parámetros requeridos.'
                }
                return Response(json.dumps(response_data), content_type='application/json')

            message = request.env['whatsapp_message_api.whatsapp_message'].search([('id', '=', message_id)])
            if not message:
                response_data = {
                    'status': 'error', 
                    'message': 'Mensaje no encontrado.'
                }
                return Response(json.dumps(response_data), content_type='application/json')

            clientId = message.chat_id.user_id.connection_id.phone_number
            fromTel = message.chat_id.phone_number
            toTel = ''
            id_message = message.serialized
            isGroup = message.chat_id.is_group
            
            if isGroup:
                fromGroup = message.chat_id.group_id.serialized
                toGroup = ''

            # Obtener la URL base de la API
            api_base_url = self._get_api_url()
            api_url = f"{api_base_url}/replyMessage"
            data = {
                'clientId': clientId,
                'fromTel': fromTel,
                'toTel': 'sent',
                'messageId': id_message,
                'fromTel': fromTel,
            }

            # Realiza la solicitud POST a la API externa
            response = requests.post(api_url, json=data)

            if response.status_code == 200:
                response_data = response.json()
                if response_data.get('success'):
                    response_data = {'status': 'success', 'message': 'Mensaje reenviado correctamente.'}
                    return Response(json.dumps(response_data), content_type='application/json')
                else:
                    response_data = {'status': 'error', 'message': response_data.get('message')}
                    return Response(json.dumps(response_data), content_type='application/json')
            else:
                _logger.error(f"Error en la respuesta de la API externa: {response.text}")
                response_data = {'status': 'error', 'message': 'Error en la respuesta de la API externa.'}
                return Response(json.dumps(response_data), content_type='application/json')
        except Exception as e:
            _logger.error(f"Error al reenviar el mensaje: {e}")
            response_data = {'status': 'error', 'message': str(e)}
            return Response(json.dumps(response_data), content_type='application/json')

    @route('/api/message/reply', type='http', auth='public', methods=['POST'], csrf=False)
    def reply_message(self):
        try:
            post = request.httprequest.get_json()
            if not post:
                response_data = {
                    'status': 'error', 
                    'message': 'No se proporcionaron datos en el cuerpo de la solicitud.'
                }
                return Response(json.dumps(response_data), content_type='application/json', status=400)

            message_id = post.get('message_id')
            reply_text = post.get('reply')

            if not message_id or not reply_text:
                response_data = {
                    'status': 'error', 
                    'message': 'Faltan parámetros requeridos.'
                }
                return Response(json.dumps(response_data), content_type='application/json')

            message = request.env['whatsapp_message_api.whatsapp_message'].search([('id', '=', message_id)])
            if not message:
                response_data = {
                    'status': 'error', 
                    'message': 'Mensaje no encontrado.'
                }
                return Response(json.dumps(response_data), content_type='application/json')

            isGroup = message.chat_id.is_group
            id_message = message.serialized
            phone_number = message.chat_id.phone_number
            id_client = message.chat_id.user_id.connection_id.phone_number

            # Obtener la URL base de la API
            api_base_url = self._get_api_url()
            api_url = f"{api_base_url}/replyMessage"
            data = {
                'clientId': id_client,
                'tel': phone_number,
                'messageId': id_message,
                'isGroup': isGroup,
                'reply': reply_text,
            }

            # Realiza la solicitud POST a la API externa
            response = requests.post(api_url, json=data)

            if response.status_code == 200:
                response_data = response.json()
                if response_data.get('success'):
                    response_data = {
                        'status': 'success', 
                        'message': 'Mensaje respondido correctamente.'
                    }
                    return Response(json.dumps(response_data), content_type='application/json')
                else:
                    response_data = {
                        'status': 'error', 
                        'message': response_data.get('message')
                    }
                    return Response(json.dumps(response_data), content_type='application/json')
            else:
                _logger.error(f"Error en la respuesta de la API externa: {response.text}")
                response_data = {
                    'status': 'error', 
                    'message': 'Error en la respuesta de la API externa.'
                }
                return Response(json.dumps(response_data), content_type='application/json')
        
        except Exception as e:
            _logger.error(f"Error al responder el mensaje: {e}")
            response_data = {
                'status': 'error', 
                'message': str(e)
            }
            return Response(json.dumps(response_data), content_type='application/json')

    @route('/api/message/reply-received', type='http', auth='public', methods=['POST'], csrf=False)
    def reply_message_received(self):
        try:
            post = request.httprequest.get_json()
            if not post:
                response_data = {
                    'status': 'error', 
                    'message': 'No se proporcionaron datos en el cuerpo de la solicitud.'
                }
                return Response(json.dumps(response_data), content_type='application/json', status=400)

            message_id = post.get('message_id')
            reply_text = post.get('reply')
            chat_id = post.get('chat_id')

            if not message_id or not reply_text:
                response_data = {
                    'status': 'error', 
                    'message': 'Faltan parámetros requeridos.'
                }
                return Response(json.dumps(response_data), content_type='application/json')

            chat = request.env['whatsapp_message_api.whatsapp_chat'].search([('id', '=', chat_id)])
            if not chat:
                response_data = {
                    'status': 'error', 
                    'message': 'Mensaje no encontrado.'
                }
                return Response(json.dumps(response_data), content_type='application/json')

            isGroup = chat.is_group
            id_message = message_id
            phone_number = chat.phone_number
            id_client = chat.user_id.connection_id.phone_number

            # Obtener la URL base de la API
            api_base_url = self._get_api_url()
            api_url = f"{api_base_url}/replyMessage"
            data = {
                'clientId': id_client,
                'tel': phone_number,
                'messageId': id_message,
                'isGroup': isGroup,
                'reply': reply_text,
            }

            # Realiza la solicitud POST a la API externa
            response = requests.post(api_url, json=data)

            if response.status_code == 200:
                response_data = response.json()
                if response_data.get('success'):
                    response_data = {
                        'status': 'success', 
                        'message': 'Mensaje respondido correctamente.'
                    }
                    return Response(json.dumps(response_data), content_type='application/json')
                else:
                    response_data = {
                        'status': 'error', 
                        'message': response_data.get('message')
                    }
                    return Response(json.dumps(response_data), content_type='application/json')
            else:
                _logger.error(f"Error en la respuesta de la API externa: {response.text}")
                response_data = {
                    'status': 'error', 
                    'message': 'Error en la respuesta de la API externa.'
                }
                return Response(json.dumps(response_data), content_type='application/json')
        
        except Exception as e:
            _logger.error(f"Error al responder el mensaje: {e}")
            response_data = {
                'status': 'error', 
                'message': str(e)
            }
            return Response(json.dumps(response_data), content_type='application/json')

    @route('/api/message/delete', type='http', auth='public', methods=['POST'], csrf=False)
    def delete_message(self):
        try:
            post = request.httprequest.get_json()
            if not post:
                response_data = {
                    'status': 'error', 
                    'message': 'No se proporcionaron datos en el cuerpo de la solicitud.'
                }
                return Response(json.dumps(response_data), content_type='application/json', status=400)

            message_id = post.get('message_id')

            if not message_id:
                response_data = {
                    'status': 'error', 
                    'message': 'Falta el parámetro requerido.'
                }
                return Response(json.dumps(response_data), content_type='application/json')

            message = request.env['whatsapp_message_api.whatsapp_message'].search([('id', '=', message_id)])
            if not message:
                response_data = {
                    'status': 'error', 
                    'message': 'Mensaje no encontrado.'
                }
                return Response(json.dumps(response_data), content_type='application/json')

            is_group = message.chat_id.is_group
            id_message = message.serialized
            phone_number = message.chat_id.phone_number
            id_client = message.chat_id.user_id.connection_id.phone_number

            # Obtener la URL base de la API
            api_base_url = self._get_api_url()
            api_url = f"{api_base_url}/deleteMessage"
            data = {
                'clientId': id_client,
                'tel': phone_number,
                'messageId': id_message,
                'isGroup': is_group,
                'forEveryone': True,  # Cambiado a booleano
            }

            # Realiza la solicitud POST a la API externa
            _logger.info(f"Enviando datos a la API externa: {data}")
            response = requests.delete(api_url, json=data)

            if response.status_code == 200:
                response_data = response.json()
                _logger.info(f"Respuesta de la API externa: {response_data}")

                if response_data.get('success'):
                    response_data = {
                        'status': 'success', 
                        'message': 'Mensaje eliminado correctamente.'
                    }
                    return Response(json.dumps(response_data), content_type='application/json')
                else:
                    response_data = {
                        'status': 'error', 
                        'message': response_data.get('message')
                    }
                    return Response(json.dumps(response_data), content_type='application/json')
            else:
                _logger.error(f"Error en la respuesta de la API externa: {response.status_code} - {response.text}")
                response_data = {
                    'status': 'error', 
                    'message': 'Error en la respuesta de la API externa.'
                }
                return Response(json.dumps(response_data), content_type='application/json')

        except Exception as e:
            _logger.error(f"Error al eliminar el mensaje: {e}")
            response_data = {
                'status': 'error', 
                'message': str(e)
            }
            return Response(json.dumps(response_data), content_type='application/json')