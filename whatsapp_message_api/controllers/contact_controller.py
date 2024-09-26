import logging
import requests
import json
import base64
from odoo import http
from odoo.exceptions import UserError
from odoo.http import request, Response

_logger = logging.getLogger(__name__)

class WhatsappContactController(http.Controller):

    def _get_api_url(self):
        try:
            api_url = request.env['ir.config_parameter'].sudo().get_param('api_base')
            if not api_url:
                raise UserError("La URL de la API no está configurada en los parámetros del sistema.")
            return api_url
        except Exception as e:
            _logger.error(f"Error al obtener la URL de la API: {e}")
            raise UserError("No se pudo obtener la URL de la API. Por favor, verifica la configuración del sistema.")

    @http.route('/api/contacts/search', type='http', auth='public', csrf=False)
    def search_contacts(self, query=""):
        """Endpoint para buscar contactos de WhatsApp."""
        try:
            domain = ['|', ('name', 'ilike', query), ('phone_number', 'ilike', query)]
            contacts = request.env['whatsapp_message_api.whatsapp_contact'].search(domain)
            contacts_data = [{
                'id': contact.id,
                'name': contact.name,
                'serialized': contact.serialized,
                'phone_number': contact.phone_number,
                'profile_pic_url': contact.profile_pic_url,
                'user_display_name': contact.user_id.display_name,
                'user_id': contact.user_id.id,
                'color': contact.user_id.connection_id.color or '#cccccc'
            } for contact in contacts]

            response_data = {
                'status': 'success', 
                'contacts': contacts_data
            }
            return Response(json.dumps(response_data), content_type='application/json')
        except Exception as e:
            _logger.error(f"Error al buscar contactos: {e}")
            response_data =  {
                'status': 'error', 
                'message': str(e)
            }
            return Response(json.dumps(response_data), content_type='application/json')
                
    @http.route('/api/contacts/save', type='json', auth='public', methods=['POST'], csrf=False)
    def save_contact(self):
        try:
            post = request.httprequest.get_json()

            if not post:
                return {
                    'status': 'error', 
                    'message': 'No se proporcionaron datos en el cuerpo de la solicitud.'
                }

            client_id = post.get('clientId')
            contact_number = post.get('contactNumber')
            contact_name = post.get('contactName')

            if not client_id or not contact_number or not contact_name:
                return {
                    'status': 'error', 
                    'message': 'Faltan parámetros requeridos.'
                }

            serialized_contact = f"{contact_number}@c.us"

            existing_contact = request.env['whatsapp_message_api.whatsapp_contact'].search([
                ('phone_number', '=', contact_number), 
                ('user_id', '=', client_id),
                ('serialized','=', serialized_contact)
            ], limit=1)

            if existing_contact:
                return {
                    'status': 'exists',
                    'message': 'El contacto ya existe en el sistema.'
                }

            user = request.env['whatsapp_message_api.whatsapp_user'].search([('id', '=', client_id)])
            if not user:
                return {
                    'status': 'error', 
                    'message': 'Usuario no encontrado.'
                }

            # Preparar los datos del contacto en el formato esperado por el método del modelo
            contact_data = {
                'id': serialized_contact, 
                'clientNumber': user.phone_number, 
                'phone_number': contact_number, 
                'name': contact_name, 
                'profilePicUrl': 'https://cdn.playbuzz.com/cdn/913253cd-5a02-4bf2-83e1-18ff2cc7340f/c56157d5-5d8e-4826-89f9-361412275c35.jpg'  
            }

            # Utilizar el método del modelo para crear o actualizar el contacto y chat asociado
            new_contact = request.env['whatsapp_message_api.whatsapp_contact'].create_or_update_contact(contact_data)

            return {
                'status': 'success',
                'message': 'Contacto guardado correctamente.',
                'reload': True,
            }

        except Exception as e:
            _logger.error(f"Error al agregar un contacto: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
        
    
    @http.route('/api/contact/add', type='json', auth='public', methods=['POST'])
    def add_contact(self):
        try:
            post = request.httprequest.get_json()
            name = post.get('name').strip() if post.get('name') else ''
            phone_number = post.get('phone_number').strip() if post.get('phone_number') else ''
            profile_pic_url = post.get('profile_pic_url')

            # Validar parámetros
            if not name or not phone_number:
                response = {
                    'status': 'error', 
                    'message': 'Faltan parámetros necesarios'
                }
                _logger.info(f'Returning response: {json.dumps(response)}')
                return response

            # Verificar si el contacto ya existe
            existing_contact = request.env['res.partner'].sudo().search([
                ('phone', '=', phone_number)
            ], limit=1)

            if existing_contact:
                response = {
                    'status': 'error', 
                    'message': 'El contacto ya existe'
                }
                _logger.info(f'Contact already exists: {existing_contact.id}')
                return response

            # Descargar y convertir la imagen a base64
            image_data = None
            if profile_pic_url:
                response = requests.get(profile_pic_url)
                if response.status_code == 200:
                    image_data = base64.b64encode(response.content).decode('utf-8')
                else:
                    _logger.warning(f'No se pudo descargar la imagen: {profile_pic_url}')

            # Crear el contacto en el modelo res.partner
            contact = request.env['res.partner'].create({
                'name': name,
                'phone': phone_number,
                'image_1920': image_data,  # Imagen de perfil en base64
            })

            response = {
                'status': 'success', 
                'contact_id': contact.id
            }
            _logger.info(f'Contacto creado: {contact.id}')
            return response

        except Exception as e:
            _logger.exception('An error occurred while adding a contact.')
            response = {
                'status': 'error', 
                'message': str(e)
            }
            _logger.info(f'Returning response: {json.dumps(response)}')
            return response

    @http.route('/api/products/search', type='http', auth='public', csrf=False)
    def search_products(self, query=""):
        """Endpoint para buscar productos por nombre."""
        try:
            # Buscar productos por nombre
            domain = [('name', 'ilike', query)]
            products = request.env['product.template'].search(domain)
            products_data = [{
                'id': product.id,
                'name': product.name,
                'list_price': product.list_price,
                'image_url': '/web/image/product.template/%d/image_1920' % product.id
            } for product in products]

            response_data = {
                'status': 'success', 
                'products': products_data
            }
            return Response(json.dumps(response_data), content_type='application/json')
        except Exception as e:
            _logger.error(f"Error al buscar productos: {e}")
            response_data = {
                'status': 'error', 
                'message': str(e)
            }
            return Response(json.dumps(response_data), content_type='application/json')
