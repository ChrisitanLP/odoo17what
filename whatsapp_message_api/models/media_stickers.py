import os
from odoo import models, fields, api
from odoo.exceptions import UserError

class WhatsappSticker(models.Model):
    _name = 'whatsapp_message_api.whatsapp_sticker'
    _description = 'Whatsapp Sticker'

    name = fields.Char('Name')
    sticker_url = fields.Text('Sticker URL')
    file_name = fields.Char('File Name')
    mime_type = fields.Char('MIME Type')
    description = fields.Text('Description') 

    @api.model
    def create_default_stickers(self):
        """Create default stickers if none exist"""
        existing_stickers = self.search([])
        if not existing_stickers:
            default_stickers = [
                {
                    'name': 'Baile',
                    'file_name': 'baile.webp',
                    'sticker_url': '/whatsapp_message_api/static/src/img/stickers/baile.webp',
                    'mime_type': 'image/webp'
                },
                {
                    'name': 'Grito',
                    'file_name': 'grito.webp',
                    'sticker_url': '/whatsapp_message_api/static/src/img/stickers/grito.webp',
                    'mime_type': 'image/webp'
                },
                {
                    'name': 'Kirbi',
                    'file_name': 'kirbi.webp',
                    'sticker_url': '/whatsapp_message_api/static/src/img/stickers/kirbi.webp',
                    'mime_type': 'image/webp'
                },
            ]
            self.create(default_stickers)

    @api.model
    def add_sticker(self, name, file_path, file_name, mime_type, description=None):
        """Agregar un nuevo sticker a la base de datos"""
        return self.create({
            'name': name,
            'file_name': file_name,
            'sticker_url': '/whatsapp_message_api/static/src/img/stickers/' + file_name,
            'mime_type': mime_type,
            'description': description,
        })

    def delete_sticker(self, sticker_id):
        """Delete a sticker by its ID"""
        sticker = self.browse(sticker_id)
        if sticker:
            sticker.unlink()
        else:
            raise UserError("Sticker not found.")
            