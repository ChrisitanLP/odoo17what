from odoo import models, fields, api
from odoo.exceptions import UserError
import base64
import os

class DefaultMessage(models.Model):
    _name = 'whatsapp_message_api.default_message'
    _description = 'Default Message'

    name = fields.Char(string='Name', required=True)
    text = fields.Text(string='Text')
    location = fields.Char(string='Location')
    location_latitude = fields.Float(string='Latitude')
    location_longitude = fields.Float(string='Longitude')
    code = fields.Char(string='Code')
    file_url = fields.Text(string='PDF File')
    file_name = fields.Char(string='File Name')
    web_url = fields.Char(string='Web Page URL')
    active = fields.Boolean(string='Active', default=True)
    type = fields.Selection([
        ('text', 'Text'),
        ('location', 'Location'),
        ('image', 'Image'),
        ('document', 'Document'),
        ('web_page', 'Web Page'),
    ], string='Type', required=True)

    @api.model
    def create_default_messages(self):
        """Crea mensajes por defecto si no existen"""
        existing_messages = self.search([])
        if not existing_messages:
            self.create([
                {'name': 'Saludo', 'text': 'Hola!!, ¿Cómo puedo ayudarte el día de hoy?.', 'type': 'text'},
                {'name': 'Localización', 'location': '1234 Company St, Business City, BC 12345',
                 'location_latitude': 37.7749, 'location_longitude': -122.4194, 'type': 'location'},
                {'name': 'Pagina Web', 'web_url': 'https://impaldiesel.com/', 'type': 'web_page'},
            ])

    @api.model
    def create_message(self, name, type, text=None, location=None, location_latitude=None, location_longitude=None, file_name=None, web_url=None, active=True):
        """Create un nuevo mensaje por defecto"""
        return self.create({
            'name': name,
            'type': type,
            'text': text,
            'location': location,
            'location_latitude': location_latitude,
            'location_longitude': location_longitude,
            'file_url': '/whatsapp_message_api/static/src/files/' + file_name,
            'file_name': file_name,
            'web_url': web_url,
            'active': active,
        })

    def update_message(self, message_id, **kwargs):
        """Actualiza un mensaje por defecto existente por medio de su ID"""
        message = self.browse(message_id)
        if message:
            message.write(kwargs)
        else:
            raise UserError("Message not found.")

    def delete_message(self, message_id):
        """Elimina un mensaje por defecto existente por medio de su ID"""
        message = self.browse(message_id)
        if message:
            message.unlink()
        else:
            raise UserError("Message not found.")