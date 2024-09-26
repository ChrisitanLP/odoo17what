from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
from ..utils.api_utils import get_request
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)

class WhatsappChat(models.Model):
    _name = 'whatsapp_message_api.whatsapp_chat'
    _description = 'Whatsapp Chat'

    serialized = fields.Char('Serialized')
    phone_number = fields.Char('Phone Number')
    name = fields.Char('Name')
    is_group = fields.Boolean('Is Group', default=False)
    timestamp = fields.Datetime('Timestamp')
    unread_count = fields.Integer('Unread Count', default=0)
    archived = fields.Boolean('Archived', default=False)
    pinned = fields.Boolean('Pinned', default=False)
    profile_pic_url = fields.Text('Profile Picture URL')

    last_message_body = fields.Text('Last Message Body')
    last_message_type = fields.Char('Last Message Type')
    
    group_id = fields.Many2one('whatsapp_message_api.whatsapp_group', string='Group', ondelete='cascade')
    user_id = fields.Many2one('whatsapp_message_api.whatsapp_user', string='User Account', ondelete='cascade')
    messages = fields.One2many('whatsapp_message_api.whatsapp_message', 'chat_id', string='Messages')
    last_sync_date = fields.Datetime('Last Sync Date')
    user_attending_id = fields.Many2one('res.users', string='Atendido por', ondelete='set null')

    status = fields.Selection([
        ('pendiente', 'Pendiente'),
        ('atendiendo', 'Atendiendo'),
        ('atendido', 'Atendido')
    ], string='Estado', default='pendiente')

    _sql_constraints = [
        ('unique_serialized', 'unique(serialized, user_id)', 'The serialized value combined with user ID must be unique.')
    ]

    @api.constrains('is_group', 'group_id')
    def _check_group_id(self):
        for record in self:
            if record.is_group and not record.group_id:
                raise ValidationError("Group chats must have a group_id.")
            if not record.is_group and record.group_id:
                raise ValidationError("Non-group chats cannot have a group_id.")

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
        try:
            chats = self.get_unread_chats()
            if chats:
                for chat in chats:
                    try:
                        self.create_chat(chat)
                    except UserError as e:
                        _logger.warning(f"Error al procesar chat: {e}")
                self.update_last_sync_date()
            else:
                _logger.error("No chats received from API.")
                raise UserError("No se pudo cargar los chats desde la API.")
        except Exception as e:
            _logger.error(f"Initial load failed: {e}")
            raise UserError("Error en la carga inicial de chats.")

    @api.model
    def incremental_load(self):
        try:
            last_sync = self.env['ir.config_parameter'].sudo().get_param('last_sync_date')
            if not last_sync:
                return self.initial_load()
            
            chats = self.get_unread_chats()
            if chats:
                for chat in chats:
                    self.create_chat(chat)
                self.update_last_sync_date()
            else:
                _logger.error("No chats received during incremental load.")
                raise UserError("No se pudo cargar los chats nuevos o actualizados desde la API.")
        except Exception as e:
            _logger.error(f"Incremental load failed: {e}")
            raise UserError("Error en la carga incremental de chats.")

    def create_chat(self, chat_data):
        # Extraer el número de teléfono del chat_data
        phone_number = chat_data['client']

        # Buscar el usuario utilizando el número de teléfono
        user = self.env['whatsapp_message_api.whatsapp_user'].search([('phone_number', '=', phone_number)], limit=1)
        user_id = user.id if user else False

        # Buscar el chat utilizando el serialized y el user_id
        chat = self.search([
            ('serialized', '=', chat_data['id']['_serialized']),
            ('user_id', '=', user_id)
        ], limit=1)

        group_id = False
        if chat_data.get('isGroup') and 'groupMetadata' in chat_data:
            group_data = chat_data['groupMetadata']
            group_id = self.env['whatsapp_message_api.whatsapp_group'].create_or_update_group(group_data)
            if isinstance(group_id, int):
                group = self.env['whatsapp_message_api.whatsapp_group'].browse(group_id)
                group_id = group.id if group else False

        # Verificar si 'timestamp' está presente
        timestamp = chat_data.get('timestamp')
        if timestamp:
            naive_datetime = datetime.utcfromtimestamp(timestamp)  # Crear datetime naive desde timestamp
        else:
            naive_datetime = datetime(2024, 1, 1)  # Asignar un valor por defecto o None

        # Extrae el valor de 'archived' de manera segura
        archived = chat_data.get('archived', False)
        pinned = chat_data.get('pinned', False)

        DEFAULT_PROFILE_PIC_URL = 'https://cdn.playbuzz.com/cdn/913253cd-5a02-4bf2-83e1-18ff2cc7340f/c56157d5-5d8e-4826-89f9-361412275c35.jpg'

        chat_values = {
            'phone_number': chat_data['id']['user'],
            'name': chat_data['name'],
            'timestamp': naive_datetime,  # Usar datetime naive
            'is_group': chat_data['isGroup'],
            'unread_count': chat_data['unreadCount'],
            'archived': archived,  # Asegúrate de que 'archived' esté presente
            'pinned': pinned,  # Asegúrate de que 'pinned' esté presente
            'last_message_body': chat_data.get('lastMessage', {}).get('body', ''),
            'last_message_type': chat_data.get('lastMessage', {}).get('type', ''),
            'group_id': group_id,
            'user_id': user_id,
            'profile_pic_url': chat_data.get('profilePicUrl', DEFAULT_PROFILE_PIC_URL),
            'last_sync_date': fields.Datetime.now() 
        }

        if chat:
            if chat.status == 'atendido':
                chat_values['status'] = 'pendiente'
            chat.write(chat_values)
        else:
            chat_values.update({'serialized': chat_data['id']['_serialized']})
            chat = self.create(chat_values)

    def get_unread_chats(self):
        try:
            api_url = self._get_api_url()
            response = get_request(f'{api_url}/unreadChats?page=1')
            if response and response.status_code == 200:
                first_page_chats = response.json().get('unreadChats', [])
                # Programar la carga asincrónica de las siguientes páginas
                self.env['ir.cron'].create({
                    'name': 'Cargar chats de WhatsApp (Páginas posteriores)',
                    'model_id': self.env.ref('whatsapp_message_api.model_whatsapp_message_api_whatsapp_chat').id,
                    'state': 'code',
                    'code': f'model._load_chats_async({2})',  # Empezar desde la página 2
                    'interval_type': 'minutes',
                    'interval_number': 1,  # Programar para que se ejecute en 1 minuto
                })
                return first_page_chats
            else:
                _logger.error(f"Failed to fetch chats on page 1, status code: {response.status_code}")
                return []
        except Exception as e:
            _logger.error(f"Error fetching chats: {e}")
            raise UserError("Error al obtener los chats desde la API.")

    @api.model
    def _load_chats_async(self, start_page):
        """Este método se ejecuta en segundo plano y carga las páginas restantes de chats."""
        api_url = self._get_api_url()
        page = start_page
        while True:
            try:
                response = get_request(f'{api_url}/unreadChats?page={page}')
                if response and response.status_code == 200:
                    chats = response.json().get('unreadChats', [])
                    if not chats:
                        _logger.info(f"No se encontraron más chats en la página {page}. Deteniendo la carga asincrónica.")
                        break  # No hay más chats, terminar la carga
                    
                    # Filtrar chats nuevos (que no existan en la BD)
                    chats_to_process = self._filter_new_chats(chats)
                    if chats_to_process:
                        _logger.info(f"Procesando {len(chats_to_process)} chats nuevos de la página {page}.")
                        # Procesar solo los chats nuevos
                        self.with_context(async_mode=True).process_chats_in_thread(chats_to_process)
                    else:
                        _logger.info(f"No hay chats nuevos en la página {page}.")

                    page += 1
                else:
                    _logger.error(f"Fallo al obtener los chats en la página {page}. Código de estado: {response.status_code}")
                    break
            except Exception as e:
                _logger.error(f"Error al cargar chats asincrónicamente en la página {page}: {e}")
                break

    @api.model
    def _filter_new_chats(self, chats):
        """Verifica si los chats ya existen en la base de datos y devuelve solo los nuevos."""
        new_chats = []
        for chat in chats:
            serialized_id = chat.get('id', {}).get('_serialized')
            phone_number = chat.get('client')

            if not serialized_id or not phone_number:
                _logger.warning(f"Chat con datos incompletos: {chat}")
                continue

            user = self.env['whatsapp_message_api.whatsapp_user'].search([('phone_number', '=', phone_number)], limit=1)
            user_id = user.id if user else False

            # Verificar si el chat ya existe en la base de datos
            existing_chat = self.search([('serialized', '=', serialized_id), ('user_id', '=', user_id)], limit=1)
            if not existing_chat:
                new_chats.append(chat)  # Agregar solo los chats que no existan
                _logger.info("Chat agregado")

        return new_chats

    @api.model
    def process_chats_in_thread(self, chats):
        """Procesa los chats recibidos dentro de un contexto seguro de Odoo."""
        for chat in chats:
            try:
                self.create_chat(chat)
            except UserError as e:
                _logger.warning(f"Error al procesar chat: {e}")


    def update_last_sync_date(self):
        """Actualiza la fecha de la última sincronización"""
        last_sync_date = fields.Datetime.now()
        self.env['ir.config_parameter'].sudo().set_param('last_sync_date', last_sync_date)
    
