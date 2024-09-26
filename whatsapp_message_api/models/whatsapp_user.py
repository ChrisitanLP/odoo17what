from odoo import models, fields, api
from odoo.exceptions import UserError
from ..utils.api_utils import get_request
import logging

_logger = logging.getLogger(__name__)

class WhatsappUser(models.Model):
    _name = 'whatsapp_message_api.whatsapp_user'
    _description = 'Whatsapp User'

    phone_number = fields.Char('Phone Number')
    display_name = fields.Char('Display Name')
    serialized = fields.Char('Serialized')
    server = fields.Char('Server')
    color = fields.Char('Color', default='#cccccc')
    chats = fields.One2many('whatsapp_message_api.whatsapp_chat', 'user_id', string='Chats')
    contacts = fields.One2many('whatsapp_message_api.whatsapp_contact', 'user_id', string='Contacts')
    connection_id = fields.Many2one('whatsapp_message_api.whatsapp_connection', string='Connection', ondelete='cascade')
    
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
    def initial_load(self):
        """Carga inicial de la información de usuario desde la API."""
        try:
            account_info_list = self.get_my_account_info()
            if account_info_list:
                for account_info in account_info_list:
                    self.create_user(account_info)
            else:
                _logger.error("No se pudo obtener la información de la cuenta.")
                raise UserError("No se pudo cargar la información del usuario desde la API.")
        except Exception as e:
            _logger.error(f"Error en la carga inicial: {e}")
            raise UserError(f"Error en la carga inicial: {e}")

    def create_user(self, user_data):
        """Crea o actualiza un registro de usuario en la base de datos y lo asocia con una conexión."""
        try:
            # Buscar la conexión correspondiente por número de teléfono
            connection = self.env['whatsapp_message_api.whatsapp_connection'].search([
                ('phone_number', '=', user_data.get('phone_number'))
            ], limit=1)

            # Si no existe una conexión con el número de teléfono, se establece como None
            connection_id = connection.id if connection else False

            # Buscar si el usuario ya existe en la base de datos
            existing_user = self.search([('serialized', '=', user_data.get('serialized'))], limit=1)
            if existing_user:
                # Actualizar el usuario existente
                existing_user.write({
                    'phone_number': user_data.get('phone_number'),
                    'display_name': user_data.get('display_name'),
                    'serialized': user_data.get('serialized'),
                    'server': user_data.get('server'),
                    'connection_id': connection_id,  # Asociar con la conexión
                })
            else:
                # Crear un nuevo usuario
                self.create({
                    'phone_number': user_data.get('phone_number'),
                    'display_name': user_data.get('display_name'),
                    'serialized': user_data.get('serialized'),
                    'server': user_data.get('server'),
                    'connection_id': connection_id,  # Asociar con la conexión
                })
        except Exception as e:
            _logger.error(f"Error al crear o actualizar el usuario: {e}")
            raise UserError(f"Error al crear o actualizar el usuario: {e}")

    @api.model
    def get_my_account_info(self):
        """Obtiene la información de la cuenta propia desde la API"""
        try:
            api_url = self._get_api_url()
            response = get_request(f'{api_url}/authenticated-accounts')
            if response and response.status_code == 200:
                return response.json().get('accounts', [])
            else:
                _logger.error("Error al obtener la información de la cuenta de la API.")
                return []
        except Exception as e:
            _logger.error(f"Error al obtener la información de la cuenta desde la API: {e}")
            raise UserError("Error al obtener la información de la cuenta desde la API.")
    


