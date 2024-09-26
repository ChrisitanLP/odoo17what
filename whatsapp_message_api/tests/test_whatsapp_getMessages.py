from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
import requests

class TestWhatsappMessage(TransactionCase):

    def setUp(self):
        super(TestWhatsappMessage, self).setUp()
        # URL de la API de prueba
        self.api_url = 'http://localhost:3000/api'
        # Crear un chat de prueba
        self.chat_model = self.env['whatsapp_message_api.whatsapp_chat']
        self.message_model = self.env['whatsapp_message_api.whatsapp_message']
        self.chat = self.chat_model.create({
            'serialized': '593979078629@c.us',
            'phone_number': '593979078629',
            'name': 'Pitajaya',
            'timestamp': '2024-07-29 17:10:30',
            'is_group': False,
            'unread_count': 0,
            'archived': False,
            'pinned': True,
            'last_message_id': 'true_593979078629@c.us_AB1E8E551F672CBF528ED36329DA80F3_out',
            'group_id': False,
            'user_id': False
        })

    def test_initial_load_creates_records(self):
        # Obtener datos reales de la API
        chat_id = self.chat.id
        response = requests.get(f'{self.api_url}/chatMessages/{chat_id}')
        if response.status_code != 200:
            self.fail(f"Error al obtener datos de la API: {response.status_code}")
        
        message_data_list = response.json().get('messages', [])

        # Llamar al método para cargar los mensajes del chat
        self.message_model.fetch_messages_for_chat(chat_id)

        for message_data in message_data_list:
            message = self.message_model.search([('serialized', '=', message_data['serialized'])])
            self.assertTrue(message, f"El mensaje con serialized ID {message_data['serialized']} no se creó o no se encontró.")
            self.assertEqual(message.body, message_data.get('body', ''), f"El cuerpo del mensaje con serialized ID {message_data['serialized']} no coincide.")
            self.assertEqual(message.from_user, message_data.get('from'), f"El remitente del mensaje con serialized ID {message_data['serialized']} no coincide.")
            self.assertEqual(message.to_user, message_data.get('to'), f"El destinatario del mensaje con serialized ID {message_data['serialized']} no coincide.")
            self.assertEqual(message.timestamp, datetime.fromtimestamp(message_data.get('timestamp')), f"La marca de tiempo del mensaje con serialized ID {message_data['serialized']} no coincide.")
            self.assertEqual(message.status, message_data.get('status', 'pending'), f"El estado del mensaje con serialized ID {message_data['serialized']} no coincide.")
            
        # Imprimir los registros creados para verificación
        print("Registros de mensajes creados:")
        for message in self.message_model.search([]):
            print(f"ID: {message.id}, Serialized: {message.serialized}, Body: {message.body}, From User: {message.from_user}, To User: {message.to_user}, Timestamp: {message.timestamp}, Status: {message.status}")
