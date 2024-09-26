import requests
import logging
from odoo import models, fields
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class WhatsappConnection(models.Model):
    _name = 'whatsapp_message_api.whatsapp_connection'
    _description = 'WhatsApp Connection'

    name = fields.Char('Connection Name', required=True)
    color = fields.Char('Color', default='#cccccc')
    phone_number = fields.Char('Phone Number', required=True)
    users = fields.One2many('whatsapp_message_api.whatsapp_user', 'connection_id', string='Users')

    _sql_constraints = [
        ('unique_name', 'unique(name)', 'El nombre de conexion debe ser único.')
    ]

    def get_all_connections(self):
        try:
            _logger.debug("Fetching all WhatsApp connections.")
            return self.search([])
        except Exception as e:
            _logger.error("An error occurred while fetching all connections: %s", str(e))
            raise UserError("Ocurrió un error al obtener las conexiones. Por favor, inténtelo de nuevo.")

    def delete_connection(self, connection_id):
        try:
            connection = self.browse(connection_id)
            if not connection.exists():
                _logger.error("Attempted to delete a non-existent connection with ID %s.", connection_id)
                raise UserError("La conexión que intentas eliminar no existe.")
            
            _logger.info("Deleting connection with ID %s.", connection_id)
            connection.unlink()
            return True
        except UserError as ue:
            raise ue
        except Exception as e:
            _logger.error("An error occurred while deleting the connection: %s", str(e))
            raise UserError("Ocurrió un error al eliminar la conexión. Por favor, inténtelo de nuevo.")

    def add_connection(self, name, phone_number, color):  
        try:
            if not phone_number:
                _logger.error("Phone number is required but not provided.")
                raise UserError("Debe proporcionar un número de teléfono.")

            # Comprobar si el número de teléfono ya existe
            existing_connection = self.search([('phone_number', '=', phone_number)])
            if existing_connection:
                _logger.error("Connection with phone number %s already exists.", phone_number)
                raise UserError("Ya existe una conexión con este número de teléfono.")
            
            # Crear una nueva conexión
            _logger.info("Creating new connection with phone number %s.", phone_number)
            return self.create({
                'name': name,
                'phone_number': phone_number,
                'color': color,
            })
        except UserError as ue:
            raise ue
        except Exception as e:
            _logger.error("An error occurred while adding the connection: %s", str(e))
            raise UserError("Ocurrió un error al agregar la conexión. Por favor, inténtelo de nuevo.")
