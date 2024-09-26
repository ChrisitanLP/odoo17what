from odoo import models, fields, api
from odoo.exceptions import UserError
from ..utils.api_utils import send_request, get_request
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)

class WhatsappMessage(models.Model):
    _name = 'whatsapp_message_api.whatsapp_message'
    _description = 'Whatsapp Message'

    serialized = fields.Char('Serialized')
    body = fields.Text('Message Body')
    from_Me = fields.Boolean('From Me')
    from_user = fields.Char('From User')
    to_user = fields.Char('To User')
    timestamp = fields.Datetime('Timestamp')
    status = fields.Selection([
        ('pending', 'Pending'),
        ('delete', 'Delete'),
        ('forwarded', 'Forwarded'),
        ('important', 'Important'),
        ('sent', 'Sent')
    ], default='pending')

    media_type = fields.Char('Media Type')
    hasMedia = fields.Boolean('Has Media')
    media_temp_url = fields.Text('Media Temp Url')
    media_base64 = fields.Text('Media Base64')
    mime_type = fields.Char('MIME Type')

    is_forwarded = fields.Boolean('Is Forwarded', default=False)

    hasQuotedMsg = fields.Boolean('Has Quoted Message')
    quoted_serialized = fields.Char('Quoted Serialized')
    quoted_from_user = fields.Char('Quoted From')
    quoted_to_user = fields.Char('Quoted To')
    quoted_body = fields.Text('Quoted Body')
    quoted_type = fields.Char('Quoted Type')
    quoted_timestamp = fields.Datetime('Quoted Timestamp')

    location_latitude = fields.Char('Location latitude')
    location_longitude = fields.Char('Location longitude')

    chat_id = fields.Many2one('whatsapp_message_api.whatsapp_chat', string='Chat', ondelete='cascade')

    _sql_constraints = [
        ('unique_serialized', 'unique(serialized)', 'The serialized value must be unique.')
    ]

    def _get_api_url(self):
        try:
            api_url = self.env['ir.config_parameter'].sudo().get_param('api_base')
            if not api_url:
                raise UserError("La URL de la API no está configurada en los parámetros del sistema.")
            return api_url
        except Exception as e:
            _logger.error(f"Error al obtener la URL de la API: {e}")
            raise UserError("No se pudo obtener la URL de la API. Por favor, verifica la configuración del sistema.")

    @api.model
    def initial_load(self, chat_id):
        """Carga inicial de todos los mensajes de un chat específico"""
        try:
            chat = self.env['whatsapp_message_api.whatsapp_chat'].browse(chat_id)
            if not chat:
                raise UserError(f"Chat con ID: {chat_id} no existe.")

            # Verifica si el chat es un singleton
            if len(chat) != 1:
                raise UserError(f"Se esperaban 1 chat, pero se encontraron {len(chat)}.")

            isGroup = chat.is_group

            if isGroup:
                messages = self.get_chat_messages_group(chat.user_id.connection_id.phone_number, chat.group_id.group_number)
            else:
                messages = self.get_chat_messages(chat.phone_number, chat.user_id.phone_number)
            
            if messages:
                for message in messages:
                    self.create_message(chat, message)
            else:
                _logger.error(f"No se recibieron mensajes para el chat {chat.display_name}.")
                raise UserError("No se pudieron cargar los mensajes desde la API.")
        except Exception as e:
            _logger.error(f"Error en la carga inicial de mensajes para el chat ID {chat_id}: {e}")
            raise UserError(f"Error en la carga inicial de mensajes: {e}")

    def create_message(self, chat, message_data):
        """Crea un nuevo registro de mensaje en la base de datos si no existe"""
        message_serialized = message_data.get('id')
        message_exists = self.search([('serialized', '=', message_serialized)], limit=1)

        # Convertir timestamp de entero a naive datetime
        timestamp = message_data.get('timestamp')
        naive_datetime = datetime.utcfromtimestamp(timestamp)  # Crear datetime naive desde timestamp

        # Convertir quoted_timestamp si está disponible
        quoted_body = message_data.get('quotedMsg', {}).get('body') if message_data.get('quotedMsg') else None
        quoted_timestamp = message_data.get('quotedMsg', {}).get('timestamp') if message_data.get('quotedMsg') else None
        quoted_naive_datetime = datetime.utcfromtimestamp(quoted_timestamp).replace(tzinfo=None) if quoted_timestamp else None

        message_values = {
            'chat_id': chat.id,
            'serialized': message_serialized,
            'body': message_data.get('body', ''),
            'from_Me': message_data.get('fromMe'),
            'from_user': message_data.get('from'),
            'to_user': message_data.get('to'),
            'timestamp': naive_datetime,
            'status': 'sent',  # o el estado apropiado según tu lógica
            'media_type': message_data.get('mediaType'),
            'hasMedia': message_data.get('isMedia', False),
            'mime_type': message_data.get('mediaMimeType'),
            'media_temp_url' : message_data.get('mediaTempUrl'),
            'media_base64': message_data.get('mediaBase64'),  
            'is_forwarded': message_data.get('isForwarded', False),
            'hasQuotedMsg': message_data.get('hasQuotedMsg', False),
            'quoted_serialized': message_data.get('quotedStanzaID'),
            'quoted_from_user': message_data.get('quotedParticipant', {}).get('_serialized', '') if message_data.get('quotedParticipant') else '',
            'quoted_to_user': message_data.get('quotedMsg', {}).get('to', '') if message_data.get('quotedMsg') else '',
            'quoted_body': quoted_body,
            'quoted_type': message_data.get('quotedMsg', {}).get('type', '') if message_data.get('quotedMsg') else '',
            'quoted_timestamp': quoted_naive_datetime,
            'location_latitude': message_data.get('location',{}).get('latitude', '') if message_data.get('location') else '',
            'location_longitude': message_data.get('location',{}).get('longitude', '') if message_data.get('location') else ''
        }

        if message_exists:
            message_exists.write(message_values)
        else:
            self.create(message_values)

    @api.model
    def get_chat_messages(self, phone_number, client_id):
        api_url = self._get_api_url()
        response = get_request(f'{api_url}/chatMessages/{client_id}/{phone_number}')
        if response and response.status_code == 200:
            return response.json().get('messages', [])
        return []

    @api.model
    def get_chat_messages_group(self, phone_number, group_id):
        api_url = self._get_api_url()
        response = get_request(f'{api_url}/chatGroupMessages/{phone_number}/{group_id}')
        if response and response.status_code == 200:
            return response.json().get('messages', [])
        return []