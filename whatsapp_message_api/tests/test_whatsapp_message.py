# -*- coding: utf-8 -*-
import unittest
from odoo.tests.common import TransactionCase
from unittest.mock import patch, Mock
from odoo import models
from requests import Request

class TestWhatsappMessage(TransactionCase):

    
    def setUp(self):
        super(TestWhatsappMessage, self).setUp()
        self.WhatsappMessage = self.env['whatsapp_message_api.whatsapp_message']
        self.WhatsappChat = self.env['whatsapp_message_api.whatsapp_chat']

    def test_send_message_success(self):
        chat = self.env['whatsapp_message_api.whatsapp_chat'].create({'phone_number': '59385184705'})
        message = self.WhatsappMessage.create({
            'chat_id': chat.id,
            'body': 'Hello, World!',
        })

        with patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {'success': True}
            message.send_message()
            self.assertEqual(message.status, 'sent')
            print("Test passed: Message status is: "+message.status)


    @patch('requests.post')
    def test_send_message(self, mock_post):
        # Simula una respuesta exitosa de la API
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'success': True}
        mock_post.return_value = mock_response

        # Crea una instancia del modelo
        chat = self.env['whatsapp_message_api.whatsapp_chat'].create({'phone_number': '59385184705'})
        message = self.WhatsappMessage.create({
            'chat_id': chat.id,
            'body': 'Hello World'
        })
        
        # Llama al método que deseas probar
        message.send_message()
        
        expected_status = 'sent'
        actual_status = message.status
        print(f"Expected status: {expected_status}, Actual status: {actual_status}")
        self.assertEqual(actual_status, expected_status)

        expected_call = {
            'url': 'http://localhost:3000/api/sendMessage',
            'json': {'tel': '59385184705', 'mensaje': 'Hello World'},
            'timeout': 10
        }
        print(f"Expected call: {expected_call}, Actual call: {mock_post.call_args}")
        mock_post.assert_called_once_with(expected_call['url'], json=expected_call['json'], timeout=expected_call['timeout'])

    @patch('requests.post')
    def test_send_message_failure(self, mock_post):
        print("Starting test_send_message_failure...")
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'success': False}
        mock_post.return_value = mock_response

        # Crea una instancia del modelo
        chat = self.env['whatsapp_message_api.whatsapp_chat'].create({'phone_number': '59385184705'})
        message = self.WhatsappMessage.create({
            'chat_id': chat.id,
            'body': 'Hello World'
        })
        
        message.send_message()
        
        expected_status = 'pending'
        actual_status = message.status
        print(f"Expected status: {expected_status}, Actual status: {actual_status}")
        self.assertEqual(actual_status, expected_status)

        expected_call = {
            'url': 'http://localhost:3000/api/sendMessage',
            'json': {'tel': '59385184705', 'mensaje': 'Hello World'},
            'timeout': 10
        }
        print(f"Test Send Message Failure: Expected call: {expected_call}, Actual call: {mock_post.call_args}")
        mock_post.assert_called_once_with(expected_call['url'], json=expected_call['json'], timeout=expected_call['timeout'])


    @patch('requests.get')
    def test_get_chats(self, mock_get):
        # Simula una respuesta exitosa de la API
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'chats': [{'id': '1', 'name': 'Chat 1'}]}
        mock_get.return_value = mock_response

        # Llama al método que deseas probar
        chats = self.WhatsappChat.get_chats()
        
        expected_chats = [{'id': '1', 'name': 'Chat 1'}]
        print(f"Expected chats: {expected_chats}, Actual chats: {chats}")
        self.assertEqual(chats, expected_chats)

        expected_call = {
            'url': 'http://localhost:3000/api/chats',
            'timeout': 10
        }
        print(f"Expected call: {expected_call}, Actual call: {mock_get.call_args}")
        mock_get.assert_called_once_with(expected_call['url'], timeout=expected_call['timeout'])

    @patch('requests.post')
    def test_send_pdf(self, mock_post):
        # Simula una respuesta exitosa de la API
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'success': True}
        mock_post.return_value = mock_response

        # Crea una instancia del modelo
        chat = self.env['whatsapp_message_api.whatsapp_chat'].create({'phone_number': '59385184705'})
        message = self.WhatsappMessage.create({
            'chat_id': chat.id,
            'directPath': '/path/to/pdf'
        })
        
        # Llama al método que deseas probar
        message.send_pdf()
        
        expected_status = 'sent'
        actual_status = message.status
        print(f"Expected status: {expected_status}, Actual status: {actual_status}")
        self.assertEqual(actual_status, expected_status)

        expected_call = {
            'url': 'http://localhost:3000/api/sendPDF',
            'json': {'tel': '59385184705', 'pdfUrl': '/path/to/pdf'},
            'timeout': 10
        }
        print(f"Expected call: {expected_call}, Actual call: {mock_post.call_args}")
        mock_post.assert_called_once_with(expected_call['url'], json=expected_call['json'], timeout=expected_call['timeout'])


    @patch('requests.post')
    def test_send_image(self, mock_post):
        # Simula una respuesta exitosa de la API
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'success': True}
        mock_post.return_value = mock_response

        # Crea una instancia del modelo
        chat = self.env['whatsapp_message_api.whatsapp_chat'].create({'phone_number': '59385184705'})
        message = self.WhatsappMessage.create({
            'chat_id': chat.id,
            'directPath': '/path/to/image'
        })
        
        # Llama al método que deseas probar
        message.send_image()
        
        expected_status = 'sent'
        actual_status = message.status
        print(f"Expected status: {expected_status}, Actual status: {actual_status}")
        self.assertEqual(actual_status, expected_status)

        expected_call = {
            'url': 'http://localhost:3000/api/sendImage',
            'json': {'tel': '59385184705', 'imgUrl': '/path/to/image'},
            'timeout': 10
        }
        print(f"Expected call: {expected_call}, Actual call: {mock_post.call_args}")
        mock_post.assert_called_once_with(expected_call['url'], json=expected_call['json'], timeout=expected_call['timeout'])

    @patch('requests.post')
    def test_send_sticker(self, mock_post):
        # Simula una respuesta exitosa de la API
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'success': True}
        mock_post.return_value = mock_response

        # Crea una instancia del modelo
        chat = self.env['whatsapp_message_api.whatsapp_chat'].create({'phone_number': '59385184705'})
        message = self.WhatsappMessage.create({
            'chat_id': chat.id,
            'directPath': '/path/to/sticker'
        })
        
        # Llama al método que deseas probar
        message.send_sticker()
        
        expected_status = 'sent'
        actual_status = message.status
        print(f"Expected status: {expected_status}, Actual status: {actual_status}")
        self.assertEqual(actual_status, expected_status)

        expected_call = {
            'url': 'http://localhost:3000/api/sendSticker',
            'json': {'tel': '59385184705', 'stickerUrl': '/path/to/sticker'},
            'timeout' : 10
        }
        print(f"Expected call: {expected_call}, Actual call: {mock_post.call_args}")
        mock_post.assert_called_once_with(expected_call['url'], json=expected_call['json'], timeout=expected_call['timeout'])

    @patch('requests.post')
    def test_send_emoji(self, mock_post):
        # Simula una respuesta exitosa de la API
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'success': True}
        mock_post.return_value = mock_response

        # Crea una instancia del modelo
        chat = self.env['whatsapp_message_api.whatsapp_chat'].create({'phone_number': '59385184705'})
        message = self.WhatsappMessage.create({
            'chat_id': chat.id,
            'body': '😊'
        })
        
        # Llama al método que deseas probar
        message.send_emoji()
        
        expected_status = 'sent'
        actual_status = message.status
        print(f"Expected status: {expected_status}, Actual status: {actual_status}")
        self.assertEqual(actual_status, expected_status)

        expected_call = {
            'url': 'http://localhost:3000/api/sendEmoji',
            'json': {'tel': '59385184705', 'emoji': '😊'},
            'timeout': 10
        }
        print(f"Expected call: {expected_call}, Actual call: {mock_post.call_args}")
        mock_post.assert_called_once_with(expected_call['url'], json=expected_call['json'], timeout=expected_call['timeout'])

    @patch('requests.get')
    def test_get_unread_chats(self, mock_get):
        # Simula una respuesta exitosa de la API
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'unreadChats': [{'id': '1', 'name': 'Chat 1'}]}
        mock_get.return_value = mock_response

        # Llama al método que deseas probar
        unread_chats = self.WhatsappChat.get_unread_chats()
        
        expected_chats = [{'id': '1', 'name': 'Chat 1'}]
        print(f"Expected unread chats: {expected_chats}, Actual unread chats: {unread_chats}")
        self.assertEqual(unread_chats, expected_chats)

        expected_call = {
            'url': 'http://localhost:3000/api/unreadChats',
            'timeout': 10
        }
        print(f"Expected call: {expected_call}, Actual call: {mock_get.call_args}")
        mock_get.assert_called_once_with(expected_call['url'], timeout=expected_call['timeout'])

    @patch('requests.get')
    def test_get_chat_messages(self, mock_get):
        # Simula una respuesta exitosa de la API
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'messages': [{'id': '1', 'body': 'Hello'}]}
        mock_get.return_value = mock_response

        # Crea una instancia del modelo
        chat = self.env['whatsapp_message_api.whatsapp_chat'].create({'phone_number': '59385184705'})
        message = self.WhatsappMessage.create({
            'chat_id': chat.id
        })
        
        # Llama al método que deseas probar
        messages = message.get_chat_messages()
        
        expected_messages = [
            {'id': '1', 'body': 'Hello'}
            ]
        print(f"Expected messages: {expected_messages}, Actual messages: {messages}")
        self.assertEqual(messages, expected_messages)

        expected_call = {
            'url':'http://localhost:3000/api/chatMessages/59385184705',
            'timeout':10
        }
        print(f"Expected call: {expected_call}, Actual call: {mock_get.call_args}")
        mock_get.assert_called_once_with(expected_call['url'], timeout=expected_call['timeout'])

    @patch('requests.get')
    def test_get_group_chat_messages(self, mock_get):
        # Simula una respuesta exitosa de la API
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'messages': [{'id': '1', 'body': 'Hello'}]}
        mock_get.return_value = mock_response

        # Llama al método que deseas probar
        chat = self.env['whatsapp_message_api.whatsapp_chat'].create({'serialized': '59385184705'})
        messages = self.WhatsappMessage.create({
            'chat_id': chat.id
        })

        messages = messages.get_group_chat_messages()
        
        expected_messages = [{'id': '1', 'body': 'Hello'}]
        print(f"Expected group chat messages: {expected_messages}, Actual group chat messages: {messages}")
        self.assertEqual(messages, expected_messages)

        expected_call = {
            'url':'http://localhost:3000/api/chatGroupMessages/59385184705',
            'timeout': 10
        }
        print(f"Expected call: {expected_call}, Actual call: {mock_get.call_args}")
        mock_get.assert_called_once_with(expected_call['url'], timeout=expected_call['timeout'])

    @patch('requests.post')
    def test_get_message_info(self, mock_post):
        # Simula una respuesta exitosa de la API
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'messageInfo': {'id': '1', 'body': 'Hello'}}
        mock_post.return_value = mock_response

        # Crea una instancia del modelo
        chat = self.env['whatsapp_message_api.whatsapp_chat'].create({'phone_number': '593985184705'})
        message = self.WhatsappMessage.create({
            'chat_id': chat.id,
            'serialized': '1'
        })
        
        # Llama al método que deseas probar
        message_info = message.get_message_info()
        
        expected_info = {'id': '1', 'body': 'Hello'}
        print(f"Expected message info: {expected_info}, Actual message info: {message_info}")
        self.assertEqual(message_info, expected_info)

        expected_call = {
            'url': 'http://localhost:3000/api/getMessageInfo',
            'json': {'tel': '593985184705', 'messageId': '1'},
            'timeout': 10
        }
        print(f"Expected call: {expected_call}, Actual call: {mock_post.call_args}")
        mock_post.assert_called_once_with(expected_call['url'], json=expected_call['json'], timeout=expected_call['timeout'])

    @patch('requests.post')
    def test_reply_to_message(self, mock_post):
        # Simula una respuesta exitosa de la API
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'success': True}
        mock_post.return_value = mock_response

        chat = self.env['whatsapp_message_api.whatsapp_chat'].create({'phone_number': '59385184705'})
        message = self.WhatsappMessage.create({
            'chat_id': chat.id,
            'serialized': '1',
            'body': 'Reply'
        })
        
        message.reply_to_message()
        
        expected_status = 'sent'
        actual_status = message.status
        print(f"Expected status: {expected_status}, Actual status: {actual_status}")
        self.assertEqual(actual_status, expected_status)

        expected_call = {
            'url': 'http://localhost:3000/api/replyMessage',
            'json': {'tel': '59385184705', 'messageId': '1', 'reply': 'Reply'},
            'timeout': 10
        }
        print(f"Expected call: {expected_call}, Actual call: {mock_post.call_args}")
        mock_post.assert_called_once_with(expected_call['url'], json=expected_call['json'], timeout=expected_call['timeout'])