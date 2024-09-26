import json
import base64
import stat
import os
import logging
from odoo import http
from odoo.http import request, Response
from odoo.exceptions import UserError

# Configura el logger
_logger = logging.getLogger(__name__)

class DefaultMessageController(http.Controller):
    
    @http.route('/api/default_message', type='http', auth='public', csrf=False)
    def list_messages(self):
        """Obtiene la lista de mensajes por defecto"""
        try:
            messages = request.env['whatsapp_message_api.default_message'].search([])
            message_data = []
            for message in messages:
                # Leer los campos y convertir datos binarios a base64
                data = message.read(['id', 'name', 'type', 'text', 'location', 'location_latitude', 'location_longitude', 'code', 'file_url', 'file_name', 'web_url', 'active'])[0]
                
                # Convertir file_url a base64
                if data.get('file_url'):
                    data['file_url'] = base64.b64encode(data['file_url']).decode('utf-8')
                
                message_data.append(data)
                
            return Response(json.dumps(message_data), content_type='application/json')
        except Exception as e:
            return Response(json.dumps({'error': str(e)}), content_type='application/json', status=500)

    @http.route('/api/default_message/<int:message_id>', type='http', auth='public', csrf=False)
    def get_message(self, message_id):
        """Obtiene un mensaje por defecto específico por su ID"""
        try:
            message = request.env['whatsapp_message_api.default_message'].browse(message_id)
            if not message.exists():
                raise UserError("El mensaje con el ID dado no existe.")
            message_data = message.read(['id', 'name', 'type', 'text', 'location', 'location_latitude', 'location_longitude', 'code', 'file_url', 'file_name', 'web_url', 'active'])[0]
            return Response(json.dumps(message_data), content_type='application/json')
        except UserError as e:
            return Response(json.dumps({'error': str(e)}), content_type='application/json', status=404)
        except Exception as e:
            return Response(json.dumps({'error': str(e)}), content_type='application/json', status=500)


    @http.route('/api/default_message/create', type='http', auth='public', csrf=False)
    def create_message(self, **kwargs):
        """Crea un nuevo mensaje por defecto"""
        try:
            file = request.httprequest.files.get('file')
            file_name = request.params.get('file_name')

            if file:
                # Define la ruta del archivo a guardar
                stickers_directory = 'sources/custom/whatsapp_message_api/static/src/files'
                file_path = os.path.join(stickers_directory, file_name)

                # Asegúrate de que el directorio exista y tenga los permisos adecuados
                self.ensure_directory_permissions(stickers_directory)

                # Guarda el archivo en la ruta especificada
                try:
                    with open(file_path, 'wb') as dest_file:
                        while True:
                            chunk = file.stream.read(8192)  # Lee en bloques de 8 KB
                            if not chunk:
                                break
                            dest_file.write(chunk)

                    # Registro de información importante sobre el archivo
                    _logger.info(f"Archivo guardado: {file_name}")

                except Exception as e:
                    _logger.error(f'Error al guardar el archivo: {str(e)}')
                    return Response(json.dumps({'error': f'Error al guardar el archivo: {str(e)}'}), content_type='application/json', status=500)

                file_url = f'/whatsapp_message_api/static/src/files/{file_name}'
            else:
                file_url = None

            name = kwargs.get('name')
            type = kwargs.get('type')
            text = kwargs.get('text')
            location = kwargs.get('location')
            location_latitude = kwargs.get('location_latitude')
            location_longitude = kwargs.get('location_longitude')
            file_url = file_url
            file_name = kwargs.get('file_name')
            web_url = kwargs.get('web_url')
            active = kwargs.get('active', True)

            # Crea el mensaje por defecto en la base de datos
            message = request.env['whatsapp_message_api.default_message'].create_message(name,type, text, location, location_latitude, location_longitude, file_name, web_url, active)

            # Obtén la lista actualizada de mensajes
            messages = request.env['whatsapp_message_api.default_message'].search([])
            message_data = []
            for message in messages:
                # Leer los campos y convertir datos binarios a base64
                data = message.read(['id', 'name', 'type', 'text', 'location', 'location_latitude', 'location_longitude', 'code', 'file_url', 'file_name', 'web_url', 'active'])[0]
                message_data.append(data)

            return Response(json.dumps({'success': True, 'messages': message_data}), content_type='application/json')
        except Exception as e:
            _logger.error(f'Error en el controlador: {str(e)}')
            return Response(json.dumps({'error': str(e)}), content_type='application/json', status=500)

    def ensure_directory_permissions(self, directory):
        """Asegúrate de que el directorio tenga los permisos adecuados"""
        if not os.path.exists(directory):
            os.makedirs(directory, mode=0o755)  # Crear el directorio con permisos 755
        else:
            # Asegúrate de que el directorio tenga permisos de escritura
            current_permissions = stat.S_IMODE(os.lstat(directory).st_mode)
            required_permissions = stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO
            if current_permissions != required_permissions:
                os.chmod(directory, required_permissions)
                _logger.info(f"Permisos del directorio ajustados: {oct(required_permissions)}")

    @http.route('/api/default_message/update/<int:message_id>', type='http', auth='public', csrf=False)
    def update_message(self, message_id, **kwargs):
        """Actualiza un mensaje por defecto existente por medio de su ID"""
        try:
            message = request.env['whatsapp_message_api.default_message'].browse(message_id)
            if not message.exists():
                raise UserError("El mensaje con el ID dado no existe.")
            message.write(kwargs)
            response_data = {
                'success': 'success', 
                'message': 'Mensaje por defecto actualizado'
            }
            return Response(json.dumps(response_data), content_type='application/json')
        except UserError as e:
            return Response(json.dumps({'error': str(e)}), content_type='application/json', status=404)
        except Exception as e:
            return Response(json.dumps({'error': str(e)}), content_type='application/json', status=500)

    @http.route('/api/default_message/delete/<int:message_id>', type='http', auth='public', csrf=False)
    def delete_message(self, message_id):
        """Elimina un mensaje por defecto existente por medio de su ID"""
        message = request.env['whatsapp_message_api.default_message'].browse(message_id)
        if not message.exists():
            raise UserError("El mensaje con el ID dado no existe.")
        message.unlink()
        response_data = {
            'success': 'success', 
            'message': 'Mensajes por defecto Eliminado'
        }
        return Response(json.dumps(response_data), content_type='application/json')

    @http.route('/api/default_message/create_default', type='http', auth='public', csrf=False)
    def create_default_messages(self):
        """Crea mensajes por defecto si no existen"""
        default_message_model = request.env['whatsapp_message_api.default_message']
        default_message_model.create_default_messages()
        response_data = {
            'success': 'success', 
            'message': 'Mensajes por defecto generados'
        }
        return Response(json.dumps(response_data), content_type='application/json')

    @http.route('/default_messages', type='http', auth='public', website=True)
    def default_messages(self):
        messages = request.env['whatsapp_message_api.default_message'].search([])
        return request.render('whatsapp_message_api.default_messages_template', {'default_messages': messages})
