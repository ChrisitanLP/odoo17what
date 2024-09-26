import logging
from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
from ..utils.api_utils import get_request

_logger = logging.getLogger(__name__)

class WhatsappContact(models.Model):
    _name = 'whatsapp_message_api.whatsapp_contact'
    _description = 'Whatsapp Contact'

    serialized = fields.Char('Serialized')
    phone_number = fields.Char('Phone Number')
    name = fields.Char('Name')
    profile_pic_url = fields.Text('Profile Pic URL')
    user_id = fields.Many2one('whatsapp_message_api.whatsapp_user', string='User Account', ondelete='cascade')

    _sql_constraints = [
        ('unique_serialized', 'unique(serialized, user_id)', 'The serialized value combined with user ID must be unique.')
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
        try:
            contacts = self.get_contacts()
            if contacts:
                for contact in contacts:
                    try:
                        self.create_or_update_contact(contact)
                    except UserError as e:
                        _logger.warning(f"Error al procesar contactos: {e}")
            else:
                _logger.error("Ningún contacto recibido desde la API.")
                raise UserError("No se pudo cargar los contactos desde la API.")
        except Exception as e:
            _logger.error(f"Initial load Contacts failed: {e}")
            raise UserError("Error en la carga inicial de contactos.")

    @api.model
    def incremental_load(self):
        try:
            last_sync = self.env['ir.config_parameter'].sudo().get_param('last_sync_date')
            if not last_sync:
                return self.initial_load()

            contacts = self.get_contacts()
            if contacts:
                for contact in contacts:
                    self.create_or_update_contact(contact)
            else:
                _logger.error("No se recibieron contactos durante la carga incremental.")
                raise UserError("No se pudo cargar los contactos nuevos o actualizados desde la API.")
        except Exception as e:
            _logger.error(f"Incremental load failed: {e}")
            raise UserError("Error en la carga incremental de contactos.")

    def create_or_update_contact(self, contact_data):
        serialized_id = contact_data.get('id')
        phone_number = contact_data.get('clientNumber')
        name = contact_data.get('name')
        phone_contact = contact_data.get('phone_number')
        profile = contact_data.get('profilePicUrl')

        if not serialized_id or not phone_number:
            _logger.warning("Contact data missing 'id' or 'clientNumber' field.")
            return

        user = self.env['whatsapp_message_api.whatsapp_user'].search([('phone_number', '=', phone_number)], limit=1)
        user_id = user.id if user else False

        contact_values = {
            'phone_number': contact_data.get('phone_number', ''),
            'name': contact_data.get('name', ''),
            'profile_pic_url': contact_data.get('profilePicUrl', 'https://cdn.playbuzz.com/cdn/913253cd-5a02-4bf2-83e1-18ff2cc7340f/c56157d5-5d8e-4826-89f9-361412275c35.jpg'),
            'user_id': user_id
        }

        contact = self.search([('serialized', '=', serialized_id), ('user_id', '=', user_id)], limit=1)

        if contact:
            contact.write(contact_values)
        else:
            contact_values.update({'serialized': serialized_id})
            contact = self.create(contact_values)

        # Lógica para crear un chat después de actualizar o crear el contacto
        self.create_or_update_chat(serialized_id, user_id, phone_contact, name, profile)

    def create_or_update_chat(self, serialized_id, user_id, phone_contact, name, profile):
        chat_model = self.env['whatsapp_message_api.whatsapp_chat']
        
        # Buscar chat existente usando serialized_id y user_id
        existing_chat = chat_model.search([
            ('serialized', '=', serialized_id),
            ('user_id', '=', user_id)
        ], limit=1)

        if not existing_chat:
            DEFAULT_PROFILE_PIC_URL = 'https://cdn.playbuzz.com/cdn/913253cd-5a02-4bf2-83e1-18ff2cc7340f/c56157d5-5d8e-4826-89f9-361412275c35.jpg'
            chat_values = {
                'phone_number': phone_contact,
                'name': name,
                'timestamp': fields.Datetime.now(),
                'is_group': False,
                'unread_count': 0,
                'archived': False,
                'pinned': False,
                'last_message_body': '',
                'last_message_type': '',
                'group_id': False,
                'user_id': user_id,
                'profile_pic_url': profile or DEFAULT_PROFILE_PIC_URL,
                'serialized': serialized_id  # Usar serialized_id proporcionado
            }
            chat_model.create(chat_values)

    @api.model
    def get_contacts(self):
        try:
            api_url = self._get_api_url()
            # Cargar la primera página de forma sincrónica
            response = get_request(f'{api_url}/getContacts?page=1')
            if response and response.status_code == 200:
                first_page_contacts = response.json().get('contacts', [])
                # Programar la carga asincrónica de las siguientes páginas
                self.env['ir.cron'].create({
                    'name': 'Cargar contactos de WhatsApp (Páginas posteriores)',
                    'model_id': self.env.ref('whatsapp_message_api.model_whatsapp_message_api_whatsapp_contact').id,
                    'state': 'code',
                    'code': f'model._load_contacts_async({2})',  # Empezar desde la página 2
                    'interval_type': 'minutes',
                    'interval_number': 1,  # Programar para que se ejecute en 1 minuto
                })
                return first_page_contacts
            else:
                _logger.error(f"Failed to fetch contacts on page 1, status code: {response.status_code}")
                return []
        except Exception as e:
            _logger.error(f"Error fetching contacts: {e}")
            raise UserError("Error al obtener la información de los contactos desde la API.")

    @api.model
    def _load_contacts_async(self, start_page):
        """Este método se ejecuta en segundo plano y carga las páginas restantes de contactos."""
        api_url = self._get_api_url()
        page = start_page
        while True:
            try:
                response = get_request(f'{api_url}/getContacts?page={page}')
                if response and response.status_code == 200:
                    contacts = response.json().get('contacts', [])
                    if not contacts:
                        _logger.info(f"No se encontraron más contactos en la página {page}. Deteniendo la carga asincrónica.")
                        break  # No hay más contactos, terminar la carga
                    
                    # Filtrar contactos nuevos (que no existan en la BD)
                    contacts_to_process = self._filter_new_contacts(contacts)
                    if contacts_to_process:
                        _logger.info(f"Procesando {len(contacts_to_process)} contactos nuevos de la página {page}.")
                        # Procesar solo los contactos nuevos
                        self.with_context(async_mode=True).process_contacts_in_thread(contacts_to_process)
                    else:
                        _logger.info(f"No hay contactos nuevos en la página {page}.")

                    page += 1
                else:
                    _logger.error(f"Fallo al obtener los contactos en la página {page}. Código de estado: {response.status_code}")
                    break
            except Exception as e:
                _logger.error(f"Error al cargar contactos asincrónicamente en la página {page}: {e}")
                break

    @api.model
    def _filter_new_contacts(self, contacts):
        """Verifica si los contactos ya existen en la base de datos y devuelve solo los nuevos."""
        new_contacts = []
        for contact in contacts:
            serialized_id = contact.get('id')
            client_number = contact.get('clientNumber')
            phone_number = contact.get('phone_number')

            if not serialized_id or not client_number:
                _logger.warning(f"Contacto con datos incompletos: {contact}")
                continue

            user = self.env['whatsapp_message_api.whatsapp_user'].search([('phone_number', '=', client_number)], limit=1)
            user_id = user.id if user else False

            # Verificar si el contacto ya existe en la base de datos
            existing_contact = self.search([('serialized', '=', serialized_id), ('user_id', '=', user_id)], limit=1)
            if not existing_contact:
                new_contacts.append(contact)  # Agregar solo los contactos que no existan
                _logger.info("Contacto agregado")
                
        return new_contacts

    @api.model
    def process_contacts_in_thread(self, contacts):
        """Procesa los contactos recibidos dentro de un contexto seguro de Odoo."""
        for contact in contacts:
            try:
                self.create_or_update_contact(contact)
            except UserError as e:
                _logger.warning(f"Error al procesar contacto: {e}")
        
    """
    def get_contacts(self):
        try:
            api_url = self._get_api_url()
            all_contacts = []
            page = 1
            while True:
                response = get_request(f'{api_url}/getContacts?page={page}')
                if response and response.status_code == 200:
                    
                    contacts = response.json().get('contacts', [])
                    if not contacts:
                        break  # Si no hay más contactos, salir del ciclo
                    all_contacts.extend(contacts)
                    page += 1  # Avanzar a la siguiente página
                else:
                    _logger.error(f"Failed to fetch contacts on page {page}, status code: {response.status_code}")
                    break
            return all_contacts
        except Exception as e:
            _logger.error(f"Error fetching contacts: {e}")
            raise UserError("Error al obtener la información de los contactos desde la API.")
    """

    """
    def get_contacts(self):
        try:
            api_url = self._get_api_url()
            page = 1
            while True:
                response = get_request(f'{api_url}/getContacts?page={page}')
                if response and response.status_code == 200:
                    return response.json().get('contacts', [])
                else:
                    _logger.error(f"Failed to fetch contacts on page {page}, status code: {response.status_code}")
                    return []
        except Exception as e:
            _logger.error(f"Error fetching contacts: {e}")
            raise UserError("Error al obtener la información de los contactos desde la API.")
    """

    """
    def get_contacts(self):
        try:
            api_url = self._get_api_url()
            response = get_request(f'{api_url}/getContacts')
            if response and response.status_code == 200:
                return response.json().get('contacts', [])
            else:
                _logger.error(f"Failed to fetch contacts, status code: {response.status_code}")
                return []
        except Exception as e:
            _logger.error(f"Error fetching contacts: {e}")
            raise UserError("Error al obtener la información de los contactos desde la API.")
    """