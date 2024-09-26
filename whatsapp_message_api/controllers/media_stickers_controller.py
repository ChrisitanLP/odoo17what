import json
import stat
import os
import logging
from odoo import http
from odoo.http import request
from odoo.exceptions import UserError
from werkzeug.wrappers import Response

# Configura el logger
_logger = logging.getLogger(__name__)


class WhatsappStickerController(http.Controller):
    
    @http.route('/api/sticker', type='http', auth='public', csrf=False)
    def list_stickers(self):
        """Obtiene la lista de stickers"""
        try:
            stickers = request.env['whatsapp_message_api.whatsapp_sticker'].search([])
            sticker_data = []
            for sticker in stickers:
                sticker_info = sticker.read(['id', 'name', 'file_name', 'sticker_url', 'mime_type', 'description'])[0]
                # Asegúrate de que la URL del sticker sea correcta
                if not sticker_info.get('sticker_url'):
                    _logger.error(f"Sticker sin URL: {sticker_info.get('name')}")
                    continue

                # Verifica si la URL es accesible
                sticker_url = request.httprequest.host_url + sticker_info['sticker_url']
                sticker_info['sticker_url'] = sticker_url

                sticker_data.append(sticker_info)
            return Response(json.dumps(sticker_data), content_type='application/json')
        except Exception as e:
            _logger.error(f'Error en list_stickers: {str(e)}')
            return Response(json.dumps({'error': str(e)}), content_type='application/json', status=500)

    @http.route('/api/sticker/<int:sticker_id>', type='http', auth='public')
    def get_sticker(self, sticker_id):
        """Obtiene un sticker específico por su ID"""
        try:
            sticker = request.env['whatsapp_message_api.whatsapp_sticker'].browse(sticker_id)
            if not sticker.exists():
                raise UserError("El sticker con el ID dado no existe.")
            sticker_data = sticker.read(['id', 'name', 'sticker_file', 'file_name', 'mime_type', 'description'])[0]
            return Response(json.dumps(sticker_data), content_type='application/json')
        except UserError as e:
            return Response(json.dumps({'error': str(e)}), content_type='application/json', status=404)
        except Exception as e:
            return Response(json.dumps({'error': str(e)}), content_type='application/json', status=500)

    @http.route('/api/sticker/create', type='http', auth='public', methods=['POST'], csrf=False)
    def create_sticker(self, **kwargs):
        """Crea un nuevo sticker"""
        try:
            name = request.params.get('name')
            file = request.httprequest.files.get('file')
            file_name = request.params.get('file_name')
            mime_type = request.params.get('mime_type')
            description = request.params.get('description', '')

            if not file:
                return Response(json.dumps({'error': 'No file uploaded'}), content_type='application/json', status=400)

            # Define la ruta del archivo a guardar
            stickers_directory = 'sources/custom/whatsapp_message_api/static/src/img/stickers'
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

            # Crea el sticker en la base de datos
            sticker = request.env['whatsapp_message_api.whatsapp_sticker'].add_sticker(
                name=name,
                file_path=file_path,
                file_name=file_name,
                mime_type=mime_type,
                description=description
            )

            return Response(json.dumps({'id': sticker.id}), content_type='application/json')
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

    @http.route('/api/sticker/delete/<int:sticker_id>', type='http', auth='public', csrf=False)
    def delete_sticker(self, sticker_id):
        """Elimina un sticker por su ID"""
        try:
            # Obtén el sticker
            sticker_model = request.env['whatsapp_message_api.whatsapp_sticker']
            sticker = sticker_model.browse(sticker_id)

            if not sticker.exists():
                return Response(json.dumps({'error': 'Sticker no encontrado'}), content_type='application/json', status=404)

            # Define la ruta del archivo a eliminar
            stickers_directory = 'sources/custom/whatsapp_message_api/static/src/img/stickers'
            file_path = os.path.join(stickers_directory, sticker.file_name)

            # Elimina el archivo del sistema de archivos
            if os.path.exists(file_path):
                os.remove(file_path)
                _logger.info(f"Archivo eliminado: {file_path}")
            else:
                _logger.warning(f"Archivo no encontrado: {file_path}")

            # Elimina el sticker de la base de datos
            sticker.unlink()

            return Response(json.dumps({'success': 'Sticker eliminado exitosamente'}), content_type='application/json')
        except UserError as e:
            return Response(json.dumps({'error': str(e)}), content_type='application/json', status=404)
        except Exception as e:
            return Response(json.dumps({'error': str(e)}), content_type='application/json', status=500)

    @http.route('/api/sticker/create_default', type='http', auth='public')
    def create_default_stickers(self):
        """Crea stickers por defecto si no existen"""
        try:
            sticker_model = request.env['whatsapp_message_api.whatsapp_sticker']
            sticker_model.create_default_stickers()
            response_data = {'success': 'Stickers por defecto creados exitosamente'}
            return Response(json.dumps(response_data), content_type='application/json')
        except Exception as e:
            return Response(json.dumps({'error': str(e)}), content_type='application/json', status=500)
            