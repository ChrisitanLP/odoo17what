import requests
import logging
from odoo import models, fields, api
import requests

_logger = logging.getLogger(__name__)

class whatsapp_message_api(models.Model):
    _name = 'whatsapp_message_api.whatsapp_message_api'
    _description = 'Whatsapp Message'

    phone_number = fields.Char('Phone Number')
    message = fields.Text('Message')
    status = fields.Selection([('pending', 'Pending'), ('sent', 'Sent')], default='pending')
    pdf_url = fields.Char('PDF URL')
    image_url = fields.Char('Image URL')
    sticker_url = fields.Char('Sticker URL')
    emoji = fields.Char('Emoji')
    message_id = fields.Char('Message ID')
    for_everyone = fields.Boolean('For Everyone', default=False)
    from_phone_number = fields.Char('From Phone Number')
    to_phone_number = fields.Char('To Phone Number')
    id_serialized = fields.Char('Serialized ID')
    type = fields.Char('Type')
    timestamp = fields.Datetime('Timestamp')
    direct_path = fields.Char('Direct Path')
    filehash = fields.Char('Filehash')
    enc_filehash = fields.Char('Encrypted Filehash')
    deprecated_mms3_url = fields.Char('Deprecated MMS3 URL')
    media_type = fields.Char('Media Type')
    media_mime_type = fields.Char('Media MIME Type')
    is_sticker = fields.Boolean('Is Sticker')
    is_media = fields.Boolean('Is Media')
    has_quoted_msg = fields.Boolean('Has Quoted Message')
    quoted_participant = fields.Char('Quoted Participant')
    quoted_stanza_id = fields.Char('Quoted Stanza ID')
    quoted_msg = fields.Text('Quoted Message')
    profile_pic_url = fields.Char('Profile Pic URL')
    group_id = fields.Char('Group ID')

    @api.model
    def uninstall_hook(self):
        """Este método se ejecutará cuando se desinstale el módulo."""
        _logger.info("Ejecutando la eliminación de conexiones en la API antes de desinstalar el módulo.")

        # Obtener todas las conexiones registradas en Odoo
        connections = self.search([])
        api_base_url = self.env['ir.config_parameter'].sudo().get_param('api_base_url')  # Asegúrate de obtener la URL base de la API
        
        for connection in connections:
            phone_number = connection.phone_number
            try:
                # Hacer la solicitud a la API externa para eliminar el cliente
                data = {'number': phone_number}
                response = requests.post(f"{api_base_url}/removeClient", json=data)
                
                if response.status_code == 200:
                    _logger.info(f"Conexión con número {phone_number} eliminada correctamente de la API externa.")
                else:
                    _logger.error(f"Error al eliminar conexión {phone_number} de la API externa. Status code: {response.status_code}")
            except Exception as e:
                _logger.error(f"Ocurrió un error al eliminar la conexión {phone_number} de la API: {e}")

        # Luego de eliminar en la API externa, eliminar las conexiones locales
        connections.unlink()

    @api.model
    def _get_api_url(self):
        api_url = self.env['ir.config_parameter'].sudo().get_param('api_base_url')
        if not api_url:
            raise ValueError("La URL de la API no está configurada en los parámetros del sistema.")
        return api_url

    def send_message(self):
        api_url = self._get_api_url()
        for record in self:
            data = {
                'tel': record.phone_number,
                'mensaje': record.message
            }
            response = requests.post(f'{api_url}/sendMessage', json=data)
            if response.status_code == 200 and response.json().get('success'):
                record.status = 'sent'
            else:
                record.status = 'pending'

    def send_pdf(self):
        api_url = self._get_api_url()
        for record in self:
            data = {
                'tel': record.phone_number,
                'pdfUrl': record.pdf_url
            }
            response = requests.post(f'{api_url}/sendPDF', json=data)
            if response.status_code == 200 and response.json().get('success'):
                record.status = 'sent'
            else:
                record.status = 'pending'

    def send_image(self):
        api_url = self._get_api_url()
        for record in self:
            data = {
                'tel': record.phone_number,
                'imgUrl': record.image_url
            }
            response = requests.post(f'{api_url}/sendImage', json=data)
            if response.status_code == 200 and response.json().get('success'):
                record.status = 'sent'
            else:
                record.status = 'pending'

    def send_sticker(self):
        api_url = self._get_api_url()
        for record in self:
            data = {
                'tel': record.phone_number,
                'stickerUrl': record.sticker_url
            }
            response = requests.post(f'{api_url}/sendSticker', json=data)
            if response.status_code == 200 and response.json().get('success'):
                record.status = 'sent'
            else:
                record.status = 'pending'

    def send_emoji(self):
        api_url = self._get_api_url()
        for record in self:
            data = {
                'tel': record.phone_number,
                'emoji': record.emoji
            }
            response = requests.post(f'{api_url}/sendEmoji', json=data)
            if response.status_code == 200 and response.json().get('success'):
                record.status = 'sent'
            else:
                record.status = 'pending'

    def get_chats(self):
        api_url = self._get_api_url()
        response = requests.get(f'{api_url}/chats')
        if response.status_code == 200:
            return response.json().get('chats')
        return []

    def get_unread_chats(self):
        api_url = self._get_api_url()
        response = requests.get(f'{api_url}/unreadChats')
        if response.status_code == 200:
            return response.json().get('unreadChats')
        return []

    def get_chat_messages(self):
        api_url = self._get_api_url()
        for record in self:
            response = requests.get(f'{api_url}/chatMessages/{record.phone_number}')
            if response.status_code == 200:
                return response.json().get('messages')
        return []

    def get_group_chat_messages(self):
        api_url = self._get_api_url()
        for record in self:
            response = requests.get(f'{api_url}/chatGroupMessages/{record.group_id}')
            if response.status_code == 200:
                return response.json().get('messages')
        return []

    def mark_chat_as_read(self):
        api_url = self._get_api_url()
        for record in self:
            response = requests.post(f'{api_url}/markChatRead/{record.phone_number}')
            return response.status_code == 200 and response.json().get('success')

    def get_message_info(self):
        api_url = self._get_api_url()
        for record in self:
            data = {
                'tel': record.phone_number,
                'messageId': record.message_id
            }
            response = requests.post(f'{api_url}/getMessageInfo', json=data)
            if response.status_code == 200:
                return response.json().get('messageInfo')
        return {}

    def reply_to_message(self):
        api_url = self._get_api_url()
        for record in self:
            data = {
                'tel': record.phone_number,
                'messageId': record.message_id,
                'reply': record.message
            }
            response = requests.post(f'{api_url}/replyMessage', json=data)
            if response.status_code == 200 and response.json().get('success'):
                record.status = 'sent'
            else:
                record.status = 'pending'

    def delete_message(self):
        api_url = self._get_api_url()
        for record in self:
            data = {
                'tel': record.phone_number,
                'messageId': record.message_id,
                'forEveryone': record.for_everyone
            }
            response = requests.post(f'{api_url}/deleteMessage', json=data)
            if response.status_code == 200 and response.json().get('success'):
                record.status = 'deleted'
            else:
                record.status = 'pending'

    def delete_message_for_me(self):
        api_url = self._get_api_url()
        for record in self:
            data = {
                'tel': record.phone_number,
                'messageId': record.message_id
            }
            response = requests.post(f'{api_url}/deleteMessageForMe', json=data)
            if response.status_code == 200 and response.json().get('success'):
                record.status = 'deleted'
            else:
                record.status = 'pending'

    def mark_message_as_important(self):
        api_url = self._get_api_url()
        for record in self:
            data = {
                'tel': record.phone_number,
                'messageId': record.message_id
            }
            response = requests.post(f'{api_url}/markMessageAsImportant', json=data)
            if response.status_code == 200 and response.json().get('success'):
                record.status = 'important'
            else:
                record.status = 'pending'

    def forward_message(self):
        api_url = self._get_api_url()
        for record in self:
            data = {
                'fromTel': record.from_phone_number,
                'toTel': record.to_phone_number,
                'messageId': record.message_id
            }
            response = requests.post(f'{api_url}/forwardMessage', json=data)
            if response.status_code == 200 and response.json().get('success'):
                record.status = 'forwarded'
            else:
                record.status = 'pending'
