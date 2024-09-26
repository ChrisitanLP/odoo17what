from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError, ValidationError
import requests
from datetime import datetime

class TestWhatsappChat(TransactionCase):

    def setUp(self):
        super(TestWhatsappChat, self).setUp()
        # URL de la API de prueba
        self.api_url = 'http://localhost:3000/api'

    def test_initial_load_creates_records(self):
        """Prueba que el método initial_load crea registros correctamente con datos reales de la API."""
        # Obtener datos reales de la API
        response = requests.get(f'{self.api_url}/chats')
        if response.status_code != 200:
            self.fail(f"Error al obtener datos de la API: {response.status_code}")

        chat_data_list = response.json().get('chats', [])

        WhatsappChat = self.env['whatsapp_message_api.whatsapp_chat']

        # Llamar al método para cargar los datos
        WhatsappChat.initial_load()

        for chat_data in chat_data_list:
            chat = WhatsappChat.search([('serialized', '=', chat_data['id']['_serialized'])])
            self.assertTrue(chat, f"El chat con serialized ID {chat_data['id']['_serialized']} no se creó o no se encontró.")
            self.assertEqual(chat.phone_number, chat_data['id']['user'], f"El número de teléfono para el chat con serialized ID {chat_data['id']['_serialized']} no coincide.")
            self.assertEqual(chat.name, chat_data['name'], f"El nombre para el chat con serialized ID {chat_data['id']['_serialized']} no coincide.")
            self.assertEqual(chat.unread_count, chat_data['unreadCount'], f"El recuento de mensajes no leídos para el chat con serialized ID {chat_data['id']['_serialized']} no coincide.")
            
            
        # Imprimir los registros creados para verificación
        print("Registros de chat creados:")
        for chat in WhatsappChat.search([]):
            print(f"ID: {chat.id}, Serialized: {chat.serialized}, Phone Number: {chat.phone_number}, Name: {chat.name}, Timestamp: {chat.timestamp}, Is Group?: {chat.is_group}, Unread Count: {chat.unread_count}, Last Message: {chat.last_message_id.id}")
